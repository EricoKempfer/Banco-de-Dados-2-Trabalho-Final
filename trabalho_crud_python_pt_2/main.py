import redis
import psycopg2
import sys

# --- Configurações de Conexão ---
REDIS_HOST = 'localhost'
REDIS_PORT = 6379

POSTGRES_DB = 'trabalho_db'
POSTGRES_USER = 'postgres'
POSTGRES_PASS = 'admin'  # <-- A SENHA QUE VOCÊ DEFINIU!
POSTGRES_HOST = 'localhost'

# =======================================================
#  FUNÇÕES DO REDIS
# =======================================================

def get_redis_connection():
    """Tenta conectar ao Redis."""
    try:
        # decode_responses=True converte as respostas de bytes para strings
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
        r.ping()
        print("✅ Conectado ao Redis com sucesso!")
        return r
    except redis.exceptions.ConnectionError as e:
        print(f"❌ ERRO: Não foi possível conectar ao Redis: {e}")
        print("   Verifique se o serviço 'sudo service redis-server start' está rodando.")
        return None

def crud_redis(r):
    """Executa o CRUD no Redis usando HASHES (melhor para objetos)."""
    if r is None:
        return

    print("\n--- Iniciando CRUD no Redis ---")
    chave = "aluno:101"

    # 1. CREATE (HSET)
    print(f"1. CREATE: Criando '{chave}'...")
    r.hset(chave, mapping={
        "nome": "Monica Tissiani",
        "disciplina": "Banco de Dados II",
        "instituicao": "Unochapecó"
    })

    # 2. READ (HGETALL)
    print(f"2. READ: Lendo '{chave}'...")
    dados = r.hgetall(chave)
    print(f"   -> Dados lidos: {dados}")

    # 3. UPDATE (HSET de novo)
    print(f"3. UPDATE: Atualizando '{chave}'...")
    r.hset(chave, "disciplina", "Banco de Dados Avançado")
    campo_atualizado = r.hget(chave, "disciplina")
    print(f"   -> Campo atualizado: {campo_atualizado}")

    # 4. DELETE (DEL)
    print(f"4. DELETE: Deletando '{chave}'...")
    r.delete(chave)
    
    # Verificação
    if not r.exists(chave):
        print(f"   -> Chave '{chave}' deletada com sucesso.")
    
    print("--- CRUD Redis Concluído ---")


# =======================================================
#  FUNÇÕES DO POSTGRESQL
# =======================================================

def get_postgres_connection():
    """Tenta conectar ao PostgreSQL."""
    try:
        conn = psycopg2.connect(
            dbname=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASS,
            host=POSTGRES_HOST
        )
        print("✅ Conectado ao PostgreSQL com sucesso!")
        return conn
    except psycopg2.OperationalError as e:
        print(f"❌ ERRO: Não foi possível conectar ao PostgreSQL: {e}")
        print("   Verifique se o serviço 'sudo service postgresql start' está rodando.")
        print("   Verifique se o nome do banco, usuário e senha estão corretos.")
        return None

def crud_postgres(conn):
    """Executa o CRUD no PostgreSQL."""
    if conn is None:
        return

    print("\n--- Iniciando CRUD no PostgreSQL ---")
    
    # O 'cursor' é quem executa os comandos SQL
    # O 'with' garante que a conexão será fechada mesmo se der erro
    with conn.cursor() as cursor:
        
        # 1. CREATE (INSERT)
        print("1. CREATE: Inserindo aluno...")
        sql_insert = "INSERT INTO alunos (nome, curso) VALUES (%s, %s) RETURNING id"
        cursor.execute(sql_insert, ("Bernardo Pegoraro", "Ciência da Computação"))
        
        # Pega o ID do aluno que acabamos de inserir
        aluno_id = cursor.fetchone()[0]
        conn.commit() # IMPORTANTE: Confirma a transação
        print(f"   -> Aluno criado com ID: {aluno_id}")

        # 2. READ (SELECT)
        print(f"2. READ: Lendo aluno com ID {aluno_id}...")
        sql_select = "SELECT nome, curso FROM alunos WHERE id = %s"
        cursor.execute(sql_select, (aluno_id,))
        aluno = cursor.fetchone()
        print(f"   -> Dados lidos: {aluno}")

        # 3. UPDATE (UPDATE)
        print(f"3. UPDATE: Atualizando aluno com ID {aluno_id}...")
        sql_update = "UPDATE alunos SET curso = %s WHERE id = %s"
        cursor.execute(sql_update, ("Sistemas de Informação", aluno_id))
        conn.commit()
        print(f"   -> Aluno atualizado.")

        # 4. DELETE (DELETE)
        print(f"4. DELETE: Deletando aluno com ID {aluno_id}...")
        sql_delete = "DELETE FROM alunos WHERE id = %s"
        cursor.execute(sql_delete, (aluno_id,))
        conn.commit()
        print(f"   -> Aluno deletado.")

    print("--- CRUD PostgreSQL Concluído ---")
    # Fecha a conexão
    conn.close()


# =======================================================
#  EXECUÇÃO PRINCIPAL
# =======================================================

def main():
    print("--- INICIANDO TRABALHO DA PROF. MONICA ---")
    
    # Executa Redis
    redis_conn = get_redis_connection()
    crud_redis(redis_conn)
    
    # Executa PostgreSQL
    postgres_conn = get_postgres_connection()
    crud_postgres(postgres_conn)
    
    print("\n--- PROGRAMA FINALIZADO ---")

if __name__ == "__main__":
    main()