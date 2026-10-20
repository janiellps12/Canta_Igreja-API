CREATE TABLE IF NOT EXISTS versao (
    id_versao int PRIMARY KEY,
    data timestamp default CURRENT_TIMESTAMP
);

-----------------
-- Música
-----------------
CREATE TABLE IF NOT EXISTS musica (
    -- Música, preferencialmente música litúrgica

    -- Identificador único
    id_musica int PRIMARY KEY,
    -- Título da música em texto plano
    titulo text not null,
    -- Letra da música em formato markdown
    letra text not null
);

-----------------
-- Livro
-----------------
CREATE TABLE IF NOT EXISTS livro (
    -- Livro de músicas

    id_livro INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo text not null -- Título do livro
);

CREATE TABLE IF NOT EXISTS editora (
    -- Editora de livros

    id_editora INTEGER PRIMARY KEY AUTOINCREMENT,
    nome text not null, -- Nome da editora
    site text not null -- Endereço eletrônico para acesso ao site da editora
);

CREATE TABLE IF NOT EXISTS edicao_livro (
    -- Edição de um livro de músicas
    id_edicao_livro INTEGER PRIMARY KEY AUTOINCREMENT,

    id_livro INTEGER not null CONSTRAINT id_livro REFERENCES livro(id_livro),
    edicao text not null, -- Nome da edição
    id_editora integer not null CONSTRAINT id_editora REFERENCES editora(id_editora), -- Editora no qual o livro foi publicado
    ano integer, -- Ano de publicação do livro
    descricao text, -- Texto informativo sobre o livro
    site text, -- Site para compra do livro

    detalhes text -- JSON
);

CREATE TABLE IF NOT EXISTS cantico_livro (
    -- Cântico do livro de cânticos
    id_musica int not null CONSTRAINT id_musica REFERENCES musica(id_musica),
    id_edicao_livro int not null CONSTRAINT id_edicao_livro REFERENCES edicao_livro(id_edicao_livro),

    indice text not null, -- Número do cântico. Pode conter texto
    ordem integer not null, -- Ordem de exibição das músicas

    PRIMARY KEY (id_musica, id_edicao_livro)
);

CREATE INDEX cantico_livro_ordem_index
    ON cantico_livro(id_edicao_livro, ordem);

CREATE TABLE IF NOT EXISTS secao_edicao_livro (
    -- Seção de um livro

    id_secao_edicao_livro INTEGER PRIMARY KEY AUTOINCREMENT,
    id_edicao_livro INTEGER not null CONSTRAINT id_edicao_livro REFERENCES edicao_livro(id_edicao_livro),
    titulo text not null, -- Título da seção
    ordem INTEGER not null
);

CREATE INDEX secao_edicao_livro_ordem_index
    ON secao_edicao_livro(id_secao_edicao_livro, ordem);

CREATE TABLE IF NOT EXISTS cantico_secao (
    -- Cântico presente em uma seção de um livro
    id_cantico_secao INTEGER PRIMARY KEY AUTOINCREMENT,

    id_secao_edicao_livro INTEGER not null CONSTRAINT id_secao_edicao_livro REFERENCES secao_edicao_livro(id_secao_edicao_livro),

    -- Chaves estrangeiras para cantico_livro
    id_musica int not null CONSTRAINT id_musica REFERENCES musica(id_musica),
    id_edicao_livro int not null CONSTRAINT id_edicao_livro REFERENCES edicao_livro(id_edicao_livro)
);
