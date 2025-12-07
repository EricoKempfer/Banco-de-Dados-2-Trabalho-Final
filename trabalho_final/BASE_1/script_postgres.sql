-- --- CRIAÇÃO DAS TABELAS (DDL) ---

-- 1. Tabela Clientes
CREATE TABLE Clientes (
    id SERIAL PRIMARY KEY,
    cpf VARCHAR(14) UNIQUE NOT NULL,
    nome VARCHAR(100) NOT NULL,
    endereco VARCHAR(150),
    cidade VARCHAR(50),
    uf CHAR(2),
    email VARCHAR(100) UNIQUE NOT NULL
);

-- 2. Tabela Produtos
CREATE TABLE Produtos (
    id SERIAL PRIMARY KEY,
    produto VARCHAR(100) NOT NULL,
    valor DECIMAL(10, 2) NOT NULL,
    quantidade INT NOT NULL,
    tipo VARCHAR(50)
);

-- 3. Tabela Compras
CREATE TABLE Compras (
    id SERIAL PRIMARY KEY,
    id_produto INT NOT NULL,
    id_cliente INT NOT NULL,
    data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_produto FOREIGN KEY (id_produto) REFERENCES Produtos(id),
    CONSTRAINT fk_cliente FOREIGN KEY (id_cliente) REFERENCES Clientes(id)
);

-- --- INSERÇÃO DE DADOS (DML) ---

-- Inserindo Clientes
INSERT INTO Clientes (cpf, nome, endereco, cidade, uf, email) VALUES
('111.222.333-44', 'Bernardo Pegoraro', 'Rua Principal, 100', 'Chapecó', 'SC', 'bernardo@email.com'),
('555.666.777-88', 'Maria Silva', 'Av. Getúlio Vargas, 500', 'Chapecó', 'SC', 'maria@email.com'),
('999.888.777-66', 'João Souza', 'Rua Nereu Ramos, 20', 'Xaxim', 'SC', 'joao@email.com');

-- Inserindo Produtos
INSERT INTO Produtos (produto, valor, quantidade, tipo) VALUES
('Notebook Dell G15', 5500.00, 10, 'Informática'),
('Mouse Logitech G Pro', 600.00, 25, 'Periféricos'),
('Monitor 24pol IPS', 850.00, 15, 'Informática'),
('Cadeira Ergonômica', 1200.00, 5, 'Móveis');

-- Inserindo Compras
-- Bernardo (ID 1) comprou Notebook (ID 1)
INSERT INTO Compras (id_cliente, id_produto, data) VALUES (1, 1, '2025-02-15 10:30:00');
-- Bernardo (ID 1) comprou Mouse (ID 2)
INSERT INTO Compras (id_cliente, id_produto, data) VALUES (1, 2, '2025-02-15 10:35:00');
-- Maria (ID 2) comprou Cadeira (ID 4)
INSERT INTO Compras (id_cliente, id_produto, data) VALUES (2, 4, '2025-02-20 14:00:00');
