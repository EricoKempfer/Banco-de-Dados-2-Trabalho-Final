# Projeto CRUD com Redis e PostgreSQL

Resumo curto

Este repositório contém um exemplo simples em Python que demonstra operações CRUD (Create, Read, Update, Delete) usando Redis e PostgreSQL. O arquivo principal é `main.py`, que: 

- conecta-se ao Redis e executa operações de hash (HSET, HGETALL, HGET, DEL);
- conecta-se ao PostgreSQL e executa operações SQL básicas em uma tabela `alunos` (INSERT, SELECT, UPDATE, DELETE);
- imprime status e mensagens úteis para ajudar no entendimento do fluxo.

Requisitos

- Python 3.8+
- Redis rodando localmente (padrão: host `localhost`, porta `6379`)
- PostgreSQL rodando localmente com o banco e credenciais configuradas conforme `main.py`
- Dependências Python: `redis`, `psycopg2` (ou `psycopg2-binary`)

Como executar (resumo rápido)

1. Instale dependências:

```bash
pip install redis psycopg2-binary
```

2. Inicie os serviços (se necessário):

```bash
sudo service redis-server start
sudo service postgresql start
```

3. Ajuste as configurações de conexão em `main.py` (nome do banco, usuário e senha) se necessário.

4. Rode o script:

```bash
python main.py
```

Observações

- O arquivo `main.py` contém valores de configuração em variáveis (ex.: `POSTGRES_PASS = 'admin'`). Não mantenha senhas em código em projetos reais.
- Certifique-se de que a tabela `alunos` exista no PostgreSQL com uma estrutura compatível (por exemplo: `id SERIAL PRIMARY KEY, nome TEXT, curso TEXT`).

Objetivo

Fornecer um exemplo didático para demonstrar a integração básica entre Redis e PostgreSQL e como realizar operações CRUD em cada um desses sistemas de armazenamento.