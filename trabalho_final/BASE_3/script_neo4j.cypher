// BASE 3 - NEO4J (Banco de Dados Orientado a Grafos)
// Objetivo: Armazenar clientes/amigos e as relações de amizade entre eles

// ========================================
// 1) LIMPAR O BANCO
// ========================================
MATCH (n) DETACH DELETE n;

// ========================================
// 2) CRIAÇÃO DOS NÓS (PESSOAS)
// ========================================

CREATE (p1:Pessoa {
    id: 1,
    cpf: "12345678900",
    nome: "Murilo"
});

CREATE (p2:Pessoa {
    id: 2,
    cpf: "98765432100",
    nome: "João"
});

CREATE (p3:Pessoa {
    id: 3,
    cpf: "55566677788",
    nome: "Ana"
});

CREATE (p4:Pessoa {
    id: 4,
    cpf: "33322211100",
    nome: "Carlos"
});

// ========================================
// 3) CRIAÇÃO DAS RELAÇÕES DE AMIZADE
// ========================================

MATCH (a:Pessoa {id: 1}), (b:Pessoa {id: 2})
CREATE (a)-[:AMIGO_DE]-(b);

MATCH (a:Pessoa {id: 1}), (b:Pessoa {id: 3})
CREATE (a)-[:AMIGO_DE]-(b);

MATCH (a:Pessoa {id: 2}), (b:Pessoa {id: 4})
CREATE (a)-[:AMIGO_DE]-(b);

// ========================================
// 4) CONSULTAS OBRIGATÓRIAS
// ========================================

// Listar todas as pessoas
MATCH (p:Pessoa)
RETURN p;

// Listar pessoas e seus amigos
MATCH (p:Pessoa)-[:AMIGO_DE]-(amigo:Pessoa)
RETURN p, amigo;

// Listar os amigos de um cliente específico (exemplo: id = 1)
MATCH (p:Pessoa {id: 1})-[:AMIGO_DE]-(amigo)
RETURN amigo;

// Listar rede inteira de amizades com profundidade
MATCH path = (p:Pessoa)-[:AMIGO_DE*1..3]-(amigo)
RETURN path;

// ========================================
// 5) PROMOVER AMIGO A CLIENTE
// ========================================

MATCH (p:Pessoa {id: 3})
SET p:Cliente
RETURN p;

// ========================================
// 6) BUSCAR APENAS CLIENTES
// ========================================

MATCH (c:Cliente)
RETURN c;

// ========================================
// 7) BUSCAR PESSOAS QUE NÃO SÃO CLIENTES
// ========================================

MATCH (p:Pessoa)
WHERE NOT p:Cliente
RETURN p;

// ========================================
// 8) INSERIR UM NOVO AMIGO
// ========================================

CREATE (p5:Pessoa {
    id: 5,
    cpf: "22211144455",
    nome: "Fernando"
});

MATCH (a:Pessoa {id: 1}), (b:Pessoa {id: 5})
CREATE (a)-[:AMIGO_DE]-(b);

// ========================================
// 9) RECOMENDAR AMIGOS DOS AMIGOS
// ========================================

MATCH (p:Pessoa {id: 1})-[:AMIGO_DE]->(amigo)-[:AMIGO_DE]->(sugestao)
WHERE sugestao.id <> 1 AND NOT (p)-[:AMIGO_DE]-(sugestao)
RETURN sugestao AS recomendacao;
