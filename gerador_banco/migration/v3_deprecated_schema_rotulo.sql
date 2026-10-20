-----------------
-- Rótulo
-----------------
CREATE TABLE IF NOT EXISTS categoria_rotulo (
    -- Categorias possíveis para rótulos
    id_categoria_rotulo INTEGER PRIMARY KEY AUTOINCREMENT,

    nome text not null, -- Nome da categoria
    descricao text not null -- Descrição
);

CREATE TABLE IF NOT EXISTS rotulo (
    -- Classificação de uma música
    id_rotulo INTEGER PRIMARY KEY AUTOINCREMENT,

    id_categoria_rotulo int not null CONSTRAINT id_categoria_rotulo REFERENCES categoria_rotulo(id_categoria_rotulo),

    nome text not null, -- Nome do rótulo
    apelido text default null, -- Nome do rótulo
    descricao text not null
);

CREATE TABLE IF NOT EXISTS rotulo_musica (
    -- Relacionamento muitos-para-muitos de música e rótulos
    id_rotulo_musica INTEGER PRIMARY KEY,  -- AUTOINCREMENT

    id_musica int not null CONSTRAINT id_musica REFERENCES musica(id_musica),
    id_rotulo int not null CONSTRAINT id_rotulo REFERENCES rotulo(id_rotulo)
);
