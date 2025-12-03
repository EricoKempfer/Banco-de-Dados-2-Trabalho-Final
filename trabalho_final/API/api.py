from fastapi import FastAPI, HTTPException
import psycopg2
from pymongo import MongoClient
from neo4j import GraphDatabase
import redis
import json

app = FastAPI()

# --- CONFIGURAÇÃO DAS CONEXÕES ---

# 1. Base Relacional (PostgreSQL) - Histórico de Compras
def get_postgres_connection():
    return psycopg2.connect(
        host="localhost", database="loja_sql", user="user", password="password"
    )

# 2. Base de Documentos (MongoDB) - Interesses
mongo_client = MongoClient("mongodb://localhost:27017/")
mongo_db = mongo_client["loja_nosql"]

# 3. Base de Grafos (Neo4j) - Amizades
neo4j_driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))

# 4. Chave-Valor (Redis) - Cache de Leitura
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)



# --- LÓGICA DE NEGÓCIO ---

@app.post("/gerar-recomendacoes/{cliente_id}")
def gerar_consolidacao(cliente_id: int):
    """
    Este endpoint atua como um ETL on-demand:
    Lê Grafos + SQL + Mongo -> Processa -> Salva no Redis
    """
    
    # PASSO 1: Buscar amigos no Neo4j
    # Retorna IDs dos amigos do cliente
    amigos_ids = []
    query_grafo = """
    MATCH (c:Cliente {id_relacional: $id})-[:AMIGO_DE]->(amigo)
    RETURN amigo.id_relacional as id_amigo
    """
    with neo4j_driver.session() as session:
        result = session.run(query_grafo, id=cliente_id)
        amigos_ids = [record["id_amigo"] for record in result]
    
    if not amigos_ids:
        return {"status": "Sem amigos para basear recomendações"}

    # PASSO 2: Buscar o que esses amigos compraram no PostgreSQL
    # Retorna lista de produtos mais comprados pelos amigos
    produtos_recomendados = []
    
    # Transformando lista Python em tupla SQL (1, 2, 3)
    if len(amigos_ids) == 1:
        amigos_tuple = f"({amigos_ids[0]})"
    else:
        amigos_tuple = tuple(amigos_ids)

    sql_query = f"""
        SELECT p.id, p.produto, count(*) as total_vendas
        FROM Compras c
        JOIN Produtos p ON c.id_produto = p.id
        WHERE c.id_cliente IN {amigos_tuple}
        GROUP BY p.id, p.produto
        ORDER BY total_vendas DESC
        LIMIT 5;
    """
    
    conn = get_postgres_connection()
    cursor = conn.cursor()
    cursor.execute(sql_query)
    compras_amigos = cursor.fetchall() # Retorna lista de tuplas [(id, nome, qtd), ...]
    cursor.close()
    conn.close()

    # PASSO 3: Buscar interesses do próprio cliente no MongoDB
    # Serve para filtrar ou ranquear melhor os produtos acima
    usuario_mongo = mongo_db["clientes"].find_one({"id_relacional": cliente_id})
    interesses = usuario_mongo.get("interesses", []) if usuario_mongo else []

    # PASSO 4: Algoritmo de Junção (Match)
    # Cruzamos o que os amigos compraram com o que o cliente gosta
    lista_final = []
    
    for prod_id, prod_nome, qtd in compras_amigos:
        # Lógica simples: Se o produto contém palavra do interesse, ganha destaque
        motivo = "Popular entre amigos"
        prioridade = 1
        
        for interesse in interesses:
            if interesse.lower() in prod_nome.lower():
                motivo = f"Seus amigos compraram e combina com seu interesse em {interesse}"
                prioridade = 2 # Alta prioridade
                break
        
        lista_final.append({
            "produto_id": prod_id,
            "nome": prod_nome,
            "motivo": motivo,
            "score": prioridade
        })

    # Ordenar pelos mais relevantes (prioridade 2 primeiro)
    lista_final.sort(key=lambda x: x['score'], reverse=True)

    # PASSO 5: Armazenar no Redis (Com TTL de 24 horas)
    chave_redis = f"recomendacao:cliente:{cliente_id}"
    dados_json = json.dumps(lista_final)
    
    # Salva no Redis
    redis_client.set(chave_redis, dados_json, ex=86400) # ex=86400 segundos (24h)

    return {
        "mensagem": "Recomendações geradas e cacheadas com sucesso", 
        "redis_key": chave_redis,
        "preview": lista_final
    }

# Para rodar: uvicorn api:app --reload
