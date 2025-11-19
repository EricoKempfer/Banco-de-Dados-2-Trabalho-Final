import psycopg2
import xml.etree.ElementTree as ET
import os

# --- 1. Configurações ---
# ATENÇÃO: Substitua estas credenciais pelas suas configurações reais do PostgreSQL
DB_HOST = "localhost"
DB_NAME = "fornecimento" 
DB_USER = "postgres"
DB_PASS = "unochapeco"
XML_FILE = "fornecimento.xml"
JOIN_KEY = "Cod_Peca" # Chave para junção no XML e SQL

def fetch_pecas_from_db():
    """Conecta ao PostgreSQL e busca todos os dados da tabela Peca."""
    pecas = {}
    try:
        conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
        cur = conn.cursor()
        
        # Seleciona todas as colunas da tabela Peca
        cur.execute("SELECT cod_peca, pnome, cor, peso, cdade FROM Peca;")
        
        # Obtém os nomes das colunas
        col_names = [desc[0] for desc in cur.description]
        
        # Mapeia as peças pelo seu código (cod_peca)
        for row in cur.fetchall():
            peca_data = dict(zip(col_names, row))
            pecas[str(peca_data['cod_peca'])] = peca_data
            
        cur.close()
        conn.close()
        print(f"✅ Dados da tabela Peca ({len(pecas)} registros) carregados do PostgreSQL.")
        
    except psycopg2.Error as e:
        print(f"❌ Erro ao conectar ou buscar dados do PostgreSQL: {e}")
        # Retorna um dicionário vazio em caso de erro
        return {}
        
    return pecas

def parse_fornecimento_xml():
    """Carrega e analisa os dados de fornecimento do arquivo XML."""
    fornecimentos = {}
    
    # Verifica se o arquivo XML existe (crie-o se não existir)
    if not os.path.exists(XML_FILE):
        print(f"❌ Arquivo '{XML_FILE}' não encontrado. Certifique-se de criá-lo.")
        return {}

    try:
        tree = ET.parse(XML_FILE)
        root = tree.getroot()
        
        for fornecimento_node in root.findall('fornecimento'):
            
            cod_peca = fornecimento_node.find(JOIN_KEY).text
            
            # Inicializa uma lista de fornecimentos para este código de peça se ainda não existir
            if cod_peca not in fornecimentos:
                fornecimentos[cod_peca] = []
                
            # Extrai todos os dados do fornecimento (exceto a chave de junção)
            f_data = {}
            for child in fornecimento_node:
                f_data[child.tag] = child.text
                
            fornecimentos[cod_peca].append(f_data)

        print(f"✅ Dados de fornecimento ({len(fornecimentos)} códigos de peça distintos) carregados do XML.")
        
    except ET.ParseError as e:
        print(f"❌ Erro ao analisar o arquivo XML: {e}")
        # Retorna um dicionário vazio em caso de erro
        return {}

    return fornecimentos

def perform_join(pecas_db, fornecimentos_xml):
    """Realiza a junção (JOIN) entre os dados do DB e do XML."""
    
    joined_data = []
    
    print("\n--- INICIANDO A JUNÇÃO ---")
    
    # Itera sobre os dados da Peça (fonte principal para o Join)
    for cod_peca, peca_data in pecas_db.items():
        
        # Verifica se existe um correspondente no XML para o código da peça
        if cod_peca in fornecimentos_xml:
            
            # A peça do DB pode ter múltiplos fornecimentos no XML
            for fornecimento in fornecimentos_xml[cod_peca]:
                
                # Combina os dados da peça e do fornecimento
                record = {
                    "PECA_NOME": peca_data['pnome'],
                    "PECA_COR": peca_data['cor'],
                    "FORNEC_COD": fornecimento['Cod_Fornec'],
                    "PROJ_COD": fornecimento['Cod_Proj'],
                    "QUANTIDADE": int(fornecimento['Quantidade'])
                }
                joined_data.append(record)
        else:
            # Caso não haja fornecimento no XML, mas se desejar um LEFT JOIN, pode-se incluir a peça
            # print(f"⚠️ Peça {cod_peca} ('{peca_data['pnome']}') não encontrada no XML.")
            pass 
            
    print(f"\n--- RESULTADO DA JUNÇÃO ({len(joined_data)} registros) ---")
    
    return joined_data

# --- 3. Execução Principal ---
if __name__ == "__main__":
    
    # 1. Obter dados do PostgreSQL
    pecas_db = fetch_pecas_from_db()
    
    # 2. Obter dados do XML
    fornecimentos_xml = parse_fornecimento_xml()
    
    # 3. Realizar a Junção
    if pecas_db and fornecimentos_xml:
        resultados = perform_join(pecas_db, fornecimentos_xml)
        
        # 4. Exibir Resultados (Exemplo de como os dados unidos se parecem)
        for i, item in enumerate(resultados[:5]): # Mostra os primeiros 5 para não lotar o console
            print(f"  {i+1}: Peça: {item['PECA_NOME']} ({item['PECA_COR']}) - Fornecedor: {item['FORNEC_COD']} - Projeto: {item['PROJ_COD']} - Qtd: {item['QUANTIDADE']}")
        if len(resultados) > 5:
             print(f"  ... e mais {len(resultados) - 5} registros.")