from fastapi import FastAPI, HTTPException
import psycopg2
from pymongo import MongoClient
from neo4j import GraphDatabase
import redis
import json

app = FastAPI(title="Sistema de Recomendação Híbrido - Trabalho Final")

# --- 1. CONFIGURAÇÃO DAS CONEXÕES ---
# Ajuste conforme suas senhas locais

def get_postgres():
    try:
        return psycopg2.connect(host="localhost", database="loja", user="postgres", password="password")
    except:
        print("Erro: Não foi possível conectar ao PostgreSQL")
        return None

# Neo4j
neo4j_driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))

# MongoDB
mongo_client = MongoClient("mongodb://localhost:27017/")
mongo_db = mongo_client["loja_nosql"]

# Redis
try:
    redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
except:
    redis_client = None
    print("Erro: Redis não encontrado")


# ==============================================================================
#  ÁREA 0: PREPARAÇÃO (Para facilitar a apresentação)
# ==============================================================================

@app.post("/setup/popular-mongodb")
def popular_mongodb():
    """
    EXECUTAR PRIMEIRO!
    Insere os dados iniciais na Base 2 (MongoDB) para que fiquem compatíveis
    com os dados que já existem no SQL e Neo4j.
    """
    collection = mongo_db["perfis_clientes"]
    collection.delete_many({}) # Limpa para não duplicar

    dados = [
        {
            "id_cliente_sql": 1, "nome_resumo": "Bernardo Pegoraro",
            "interesses": {"geral": ["tecnologia", "games"], "produtos": ["mouse", "notebook", "informática"]}
        },
        {
            "id_cliente_sql": 2, "nome_resumo": "Maria Silva",
            "interesses": {"geral": ["conforto", "decoração"], "produtos": ["cadeira", "móveis"]}
        },
        {
            "id_cliente_sql": 3, "nome_resumo": "João Souza",
            "interesses": {"geral": ["escritório"], "produtos": ["monitor", "periféricos"]}
        }
    ]
    collection.insert_many(dados)
    return {"status": "MongoDB populado com dados de teste!"}


# ==============================================================================
#  ÁREA 1: SINCRONIZAÇÃO (ETL) - Requisito: "Atualização a partir da API"
# ==============================================================================

@app.post("/admin/sincronizar-cache-redis")
def sincronizar_tudo():
    """
    Lê as Bases 1, 2 e 3 e consolida os relatórios na Base 4 (Redis).
    Deve ser chamado sempre que houver mudanças nos bancos originais.
    """
    if not redis_client: return {"erro": "Redis offline"}

    try:
        # 1. Limpa dados antigos de relatório
        chaves = redis_client.keys("relatorio:*")
        if chaves: redis_client.delete(*chaves)
        
        conn = get_postgres()
        cursor = conn.cursor()

        # A. Cache: Lista de Clientes (Vem do SQL)
        cursor.execute("SELECT id, nome, email, cidade, uf FROM Clientes")
        clientes = [{"id": r[0], "nome": r[1], "email": r[2], "cidade": r[3], "uf": r[4]} for r in cursor.fetchall()]
        redis_client.set("relatorio:todos_clientes", json.dumps(clientes))

        # B. Cache: Histórico de Compras (Vem do SQL com Join)
        cursor.execute("""
            SELECT c.nome, p.produto, co.data 
            FROM Compras co 
            JOIN Clientes c ON co.id_cliente = c.id
            JOIN Produtos p ON co.id_produto = p.id
        """)
        historico = [{"cliente": r[0], "produto": r[1], "data": str(r[2])} for r in cursor.fetchall()]
        redis_client.set("relatorio:clientes_compras", json.dumps(historico))

        # C. Cache: Amizades (Vem do Neo4j)
        amizades = []
        with neo4j_driver.session() as session:
            result = session.run("MATCH (p:Pessoa)-[:AMIGO_DE]-(a:Pessoa) RETURN p.nome as pessoa, a.nome as amigo")
            for r in result:
                amizades.append({"cliente": r["pessoa"], "amigo": r["amigo"]})
        redis_client.set("relatorio:clientes_amigos", json.dumps(amizades))
        
        cursor.close()
        conn.close()

        return {"status": "Sucesso. Redis atualizado com dados consolidados das 3 bases."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==============================================================================
#  ÁREA 2: INTERFACE DE CONSULTA - Requisito: "Mostrar dados da base chave-valor"
# ==============================================================================

@app.get("/interface/clientes")
def ver_clientes():
    dado = redis_client.get("relatorio:todos_clientes")
    return json.loads(dado) if dado else {"aviso": "Cache vazio. Execute /admin/sincronizar-cache-redis"}

@app.get("/interface/compras-realizadas")
def ver_compras():
    dado = redis_client.get("relatorio:clientes_compras")
    return json.loads(dado) if dado else {"aviso": "Cache vazio."}

@app.get("/interface/rede-amigos")
def ver_amigos():
    dado = redis_client.get("relatorio:clientes_amigos")
    return json.loads(dado) if dado else {"aviso": "Cache vazio."}

@app.get("/interface/ver-recomendacao/{cliente_id}")
def ver_recomendacao(cliente_id: int):
    # Mostra a recomendação já processada para um amigo/cliente
    chave = f"recomendacao:cliente:{cliente_id}"
    dado = redis_client.get(chave)
    return json.loads(dado) if dado else {"aviso": "Nenhuma recomendação gerada. Execute POST /gerar-recomendacao"}


# ==============================================================================
#  ÁREA 3: MOTOR DE RECOMENDAÇÃO (INTEGRAÇÃO TOTAL)
# ==============================================================================

@app.post("/gerar-recomendacao/{cliente_id}")
def processar_recomendacao(cliente_id: int):
    """
    O Coração do sistema:
    1. Acha amigos (Neo4j)
    2. Vê o que compraram (SQL)
    3. Filtra por interesses (Mongo)
    4. Salva resultado (Redis)
    """
    
    # --- Passo 1: Neo4j ---
    amigos_ids = []
    with neo4j_driver.session() as session:
        # Busca IDs dos amigos do cliente
        res = session.run("MATCH (p:Pessoa {id: $id})-[:AMIGO_DE]-(a) RETURN a.id as id_amigo", id=cliente_id)
        amigos_ids = [r["id_amigo"] for r in res]

    if not amigos_ids:
        return {"status": "Cliente sem amigos cadastrados no grafo."}

    # --- Passo 2: PostgreSQL ---
    # Busca produtos mais comprados por esses amigos
    amigos_tuple = tuple(amigos_ids) if len(amigos_ids) > 1 else f"({amigos_ids[0]})"
    conn = get_postgres()
    cursor = conn.cursor()
    
    query = f"""
        SELECT p.id, p.produto, p.tipo, count(*) as qtd
        FROM Compras c JOIN Produtos p ON c.id_produto = p.id
        WHERE c.id_cliente IN {amigos_tuple}
        GROUP BY p.id, p.produto, p.tipo
        ORDER BY qtd DESC LIMIT 5
    """
    cursor.execute(query)
    produtos_amigos = cursor.fetchall()
    cursor.close()
    conn.close()

    # --- Passo 3: MongoDB ---
    # Busca interesses para dar "peso" à recomendação
    interesses = []
    doc = mongo_db["perfis_clientes"].find_one({"id_cliente_sql": cliente_id})
    if doc and "interesses" in doc:
        for lista in doc["interesses"].values():
            if isinstance(lista, list):
                interesses.extend([x.lower() for x in lista])

    # --- Passo 4: Algoritmo de Match ---
    recomendacoes = []
    for pid, nome, tipo, qtd in produtos_amigos:
        score = 1
        motivo = "Popular entre amigos"
        
        # Verifica se bate com interesse
        if any(i in nome.lower() for i in interesses) or any(i in tipo.lower() for i in interesses):
            score = 3
            motivo = f"Combina com seus interesses e seus amigos compraram"
        
        recomendacoes.append({
            "produto": nome,
            "motivo": motivo,
            "score_relevancia": score
        })
    
    # Ordena pelo score
    recomendacoes.sort(key=lambda x: x['score_relevancia'], reverse=True)

    # --- Passo 5: Salvar no Redis ---
    chave = f"recomendacao:cliente:{cliente_id}"
    redis_client.set(chave, json.dumps(recomendacoes))

    return {
        "status": "Processado com sucesso",
        "amigos_analisados": len(amigos_ids),
        "recomendacoes_geradas": recomendacoes
    }