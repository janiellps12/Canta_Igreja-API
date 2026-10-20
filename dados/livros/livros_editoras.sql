-----------------
-- Livro
-----------------
INSERT INTO livro (id_livro, titulo) values
    (1, 'Animados pela Fé'),
    (2, 'Cantando os Apelos da Eucaristia'),
    (3, 'Louvemos o Senhor'),
    (4, 'Músicas das Campanhas da Fraternidade 1970-2014'),
    (5, 'Carderno de cifras e partituras - Celebrações Penintenciais e Celebrações da Palavra durante a Quaresma'),
    (6, 'Caderno de Cifras e Partituras - Quaresma e Iniciação a Vida Cristã'),
    (7, 'Alegres Cantemos - Músicas para cantar a Liturgia')
;

INSERT INTO editora (id_editora, nome, site) values
    (1, 'Editora O Lutador', 'http://olutador.org.br/'),
    (2, 'Associação Do Senhor Jesus', 'https://www.rs21.com.br/site/asj/'),
    (3, 'CNBB', 'https://www.edicoescnbb.com.br/'),
    (4, 'PAULUS', 'https://www.paulus.com.br/portal/')
;

-- edicao_livro: informações apresentadas em dados/obras/.../.../informacoes.yml