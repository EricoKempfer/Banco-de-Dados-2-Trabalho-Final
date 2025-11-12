1. Configuração do Ambiente Python e Dependências

O projeto começa com a preparação do ambiente de execução. Primeiramente é necessário instalar o Python, caso ainda não esteja disponível. 

Comando para instalação do Python:
sudo apt install python3 python3-pip

Em seguida, deve-se criar um diretório para o projeto para organizar todos os arquivos.

Dentro deste diretório é fundamental criar uma Venv (ambiente virtual). A Venv (Virtual Environment) isola as dependências do projeto, garantindo que as bibliotecas instaladas não interfiram em outras instalações do Python.

Comando para criação da Venv:
python3 -m venv venv 

Após a criação é necessário ativar o ambiente virtual.

Comando para ativação (Linux/macOS):
source venv/bin/activate

Com a Venv ativa a biblioteca de conexão com o banco de dados é instalada. É necessário instalar a biblioteca do Neo4j.

Comando de instalação:
pip install neo4j

2. Configuração da IDE e Teste de Conexão

Agora vamos focar na preparação do servidor e na escrita do código. A instância do Neo4j deve ser iniciada, garantindo que o servidor esteja pronto para aceitar conexões via protocolo Bolt.

Comando de ativação da venv:
source venv/bin/activate

Para o desenvolvimento foi escolhido o VSCode. 

Deve-se instalar a extensão para o Python no VSCode para obter suporte a linting e debugging. 

Nome da extensão dentro do VSCode:
Python

Com a extensão instalada a pasta do projeto deve ser aberta no VSCode e o interpretador Python ajustado para usar a Venv recém-criada.

Por fim, deve-se criar um novo arquivo Python (ConexaoNeoj.py) e usar o código de conexão a seguir.
bolt://localhost:7687", auth=("neo4j", "unochapeco")

Após isso, o código deve ser executado para ser testado e confirmar a conectividade com o Neo4j.

Exemplo do Bloco de Código:
from neo4j import GraphDatabase

# ... (criação do driver e autenticação) ...
driver.verify_connectivity()

with driver.session(database="neo4j") as session:
    result = session.run("MATCH (p:Pessoa) RETURN p.nome AS nome")
    for record in result:
        print(record["nome"]) # <-- Indentação correta
        
driver.close()

3. Pesquisa Técnica e Referenciação

11) Pergunte a uma IA qualquer quais são os métodos da classe drive que são usados na biblioteca do neo4j em python, dando exemplos de cada um deles.

1. Método session()
O método session() é usado para criar e abrir um canal de comunicação com o banco de dados. Todas as operações de leitura e escrita (transações) devem ser executadas dentro de uma sessão.
Função: Cria uma nova sessão. É altamente recomendável usá-lo em um bloco with para garantir que a sessão seja fechada automaticamente após o uso.
Exemplo de Uso:
# O 'driver' foi criado anteriormente
# driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "senha"))

# Abre uma nova sessão. O bloco 'with' garante o fechamento.
with driver.session(database="neo4j") as session:
    # A sessão é usada para executar comandos Cypher
    session.run("CREATE (n:Produto {nome: 'Cafeteira'})") 
    print("Dados criados na sessão.")
# Ao sair do bloco 'with', a sessão é encerrada.

2. Método close()
O método close() é fundamental para o gerenciamento de recursos. Ele é chamado quando o aplicativo encerra todas as suas interações com o banco de dados.
Função: Encerra o pool de conexões de rede mantido pelo Driver. Isso libera os recursos do sistema associados à comunicação persistente com o servidor Neo4j.
Exemplo de Uso:
# ... Código de operações e transações ...

# Chamado ao final do script, após todas as sessões terem sido encerradas.
driver.close()
print("Driver fechado e conexões liberadas.")

E por último, o texto gerado pela IA foi referenciado na documentação seguindo uma adaptação de normas acadêmicas para fontes de Modelos de Linguagem de Grande Escala, garantindo a rastreabilidade da pesquisa:

Referência Adicionada ao Projeto:

Google (2025, 11 de novembro). Resposta ao prompt "Quais são os métodos da classe driver que são usados na biblioteca do neo4j em python, dando exemplos de cada um deles?" Gemini, Modelo de linguagem grande.
