from pymongo import MongoClient, ASCENDING
from datetime import datetime

class GestorBaseDocumentos:
    def __init__(self):
        # Conexão com o servidor local
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client["loja_nosql"]
        self.collection = self.db["perfis_clientes"]
        
        # Garante a criação de índices ao iniciar (Performance)
        self._criar_indices()

    def _criar_indices(self):

        # Cria índices para garantir unicidade e velocidade na busca.

        # Garante que não teremos dois documentos para o mesmo cliente SQL
        self.collection.create_index([("id_cliente_sql", ASCENDING)], unique=True)
        
        # Acelera a busca por interesses (ex: "Quem gosta de Futebol?")
        self.collection.create_index([("interesses.esportes", ASCENDING)])
        self.collection.create_index([("interesses.filmes", ASCENDING)])

    def criar_ou_atualizar_perfil(self, id_sql, nome, dados_iniciais=None):

        # Cria o documento base. Se já existir, atualiza apenas o nome.

        if dados_iniciais is None:
            dados_iniciais = {}

        filtro = {"id_cliente_sql": id_sql}
        
        # Estrutura padrão caso seja um insert
        novo_doc = {
            "$setOnInsert": {
                "interesses": {
                    "esportes": [], "filmes": [], "musica": [], "geral": []
                },
                "score_engajamento": 0
            },
            "$set": {
                "nome_resumo": nome,
                "data_atualizacao": datetime.utcnow()
            }
        }
        
        # Upsert=True: Se não existe, cria. Se existe, atualiza.
        self.collection.update_one(filtro, novo_doc, upsert=True)
        print(f"Perfil do cliente {id_sql} sincronizado no MongoDB.")

    def adicionar_interesse(self, id_sql, categoria, novo_interesse):
        """
        Adiciona um interesse sem duplicar (uso do $addToSet).
        Categorias aceitas: 'esportes', 'filmes', 'musica', 'geral'.
        """
        filtro = {"id_cliente_sql": id_sql}
        
        # $addToSet garante que não teremos ["Vôlei", "Vôlei"] repetido
        atualizacao = {
            "$addToSet": {f"interesses.{categoria}": novo_interesse},
            "$set": {"data_atualizacao": datetime.utcnow()}
        }
        
        resultado = self.collection.update_one(filtro, atualizacao)
        
        if resultado.modified_count > 0:
            print(f"Interesse '{novo_interesse}' adicionado em '{categoria}' para o cliente {id_sql}.")
        else:
            print("Interesse já existia ou cliente não encontrado.")

    def recuperar_interesses(self, id_sql):

        # Retorna uma lista plana de todos os interesses para o algoritmo de recomendação.

        doc = self.collection.find_one({"id_cliente_sql": id_sql})
        
        if not doc:
            return []
        
        # Achata o objeto em uma lista única para facilitar o match
        lista_tags = []
        interesses = doc.get("interesses", {})
        for categoria in interesses:
            lista_tags.extend(interesses[categoria])
            
        return lista_tags

# --- EXEMPLO DE USO ---
if __name__ == "__main__":
    mongo_mgr = GestorBaseDocumentos()

    # 1. Criar perfil (normalmente chamado após o cadastro no SQL)
    mongo_mgr.criar_ou_atualizar_perfil(1050, "Carlos Silva")

    # 2. Adicionar Interesses (pode vir de um form no front-end)
    mongo_mgr.adicionar_interesse(1050, "esportes", "Futebol")
    mongo_mgr.adicionar_interesse(1050, "esportes", "Basquete")
    mongo_mgr.adicionar_interesse(1050, "filmes", "Star Wars")
    
    # Tentar adicionar repetido (não fará nada)
    mongo_mgr.adicionar_interesse(1050, "esportes", "Futebol")

    # 3. Consultar (simulando a etapa da API de recomendação)
    tags = mongo_mgr.recuperar_interesses(1050)
    print(f"Tags recuperadas para recomendação: {tags}")