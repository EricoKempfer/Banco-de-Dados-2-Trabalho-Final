(:
CREATE DB fornecimento_db pecas.xml
:)

(: ------------------------------------------------------------------------- :)
(: A) Retornar os dados da penúltima peça da árvore XML. - Arquivo: pecas.xml :)
(: ------------------------------------------------------------------------- :)

(:
doc("pecas.xml")/dados/fornecimento[last() - 1]
:)
(: ------------------------------------------------------------------------- :)
(: B) Inserir um atributo com a data em todos os fornecimentos. (XQuery Update) :)
(: ------------------------------------------------------------------------- :)

(:
xquery version "3.1";
declare default element namespace "http://www.w3.org/2005/xquery-update";

for $f in doc("pecas.xml")/dados/fornecimento
return
  insert attribute data {"2025-11-18"} into $f
:)

(: ------------------------------------------------------------------------- :)
(: C) Atualizar o status dos fornecedores de Londres para 50. (XQuery Update) :)
(: ------------------------------------------------------------------------- :)

(:
xquery version "3.1";
declare default element namespace "http://www.w3.org/2005/xquery-update";

for $f in doc("fornecedores.xml")/dados/fornecedor[Cidade = 'LONDRES']
return
  replace value of node $f/Status with 50
:)

(: ------------------------------------------------------------------------- :)
(: D) Retornar o código, a cidade e cor de todas as peças. - Arquivo: pecas.xml :)
(: ------------------------------------------------------------------------- :)

(:
for $p in doc("pecas.xml")/dados/peca
return
  <peca_info>
    {$p/Cod_Peca}
    {$p/Cidade}
    {$p/Cor}
  </peca_info>
:)

(: ------------------------------------------------------------------------- :)
(: E) Obter o somatório das quantidades dos fornecimentos. - Arquivo: fornecimentos.xml :)
(: ------------------------------------------------------------------------- :)

(:
sum(doc("fornecimentos.xml")/dados/fornecimento/Quantidade)
:)

(: ------------------------------------------------------------------------- :)
(: F) Obter os nomes dos projetos de Paris. - Arquivo: projetos.xml (Presumido) :)
(: ------------------------------------------------------------------------- :)

(:
doc("projetos.xml")/dados/projeto[Cidade = 'PARIS']/PNome
:)

(: ------------------------------------------------------------------------- :)
(: G) Obter o código dos fornecedores que forneceram pecas em maior quantidade. - Arquivo: fornecimentos.xml :)
(: ------------------------------------------------------------------------- :)

(:
let $fornecimentos := doc("fornecimentos.xml")/dados/fornecimento
let $max_qtd := max($fornecimentos/Quantidade)
return
  distinct-values($fornecimentos[Quantidade = $max_qtd]/Cod_Fornec)
:)

(: ------------------------------------------------------------------------- :)
(: H) Excluir os projetos da cidade de Atenas. (XQuery Update) - Arquivo: projetos.xml (Presumido) :)
(: ------------------------------------------------------------------------- :)

(:
xquery version "3.1";
declare default element namespace "http://www.w3.org/2005/xquery-update";

delete doc("projetos.xml")/dados/projeto[Cidade = 'ATENAS']
:)

(: ------------------------------------------------------------------------- :)
(: I) Obter os nomes das peças e seus dados de fornecimento. - Arquivos: pecas.xml e fornecimentos.xml :)
(: ------------------------------------------------------------------------- :)

(:
for $p in doc("pecas.xml")/dados/peca
let $cod_peca := $p/Cod_Peca/text()
let $fornecimentos := doc("fornecimentos.xml")/dados/fornecimento[Cod_Peca = $cod_peca]
where exists($fornecimentos)
return
  <peca_e_fornecimento>
    {$p/PNome}
    <fornecimentos>
      {$fornecimentos}
    </fornecimentos>
  </peca_e_fornecimento>
:)

(: ------------------------------------------------------------------------- :)
(: J) Obter o preço médio das peças. - Arquivo: pecas.xml :)
(: ------------------------------------------------------------------------- :)

avg(doc("pecas.xml")/dados/peca/Preco)
