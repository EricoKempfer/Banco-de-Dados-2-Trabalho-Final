from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "unochapeco"))
              
# Verifica conectividade
driver.verify_connectivity()

# Abre sessão e executa query
with driver.session(database="neo4j") as session:
    result = session.run("MATCH (p:Pessoa) RETURN p.nome AS nome")
    for record in result:      
        print(record["nome"])

# Fecha conexão
driver.close()