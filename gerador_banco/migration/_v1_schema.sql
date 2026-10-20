-----------------
-- Mídia
-----------------
CREATE TABLE IF NOT EXISTS tipo_midia (
    -- Tipo de mídia, refere-se a algum conteúdo relacionado a uma música, geralmente um link do Youtube, uma partitura, etc

    -- Identificador único
    id_tipo_midia int PRIMARY KEY,
    -- Nome
    nome text not null,
    -- Descrição
    descricao text not null
);

CREATE TABLE IF NOT EXISTS midia_musica (
    -- Mídia de uma música

    -- Identificador único
    id_midia_musica INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Música
    id_musica int not null CONSTRAINT id_musica REFERENCES musica(id_musica),

    -- Mídia
    id_tipo_midia int not null CONSTRAINT id_tipo_midia REFERENCES tipo_midia(id_tipo_midia),

    -- Endereço para acesso a mídia informada
    url text not null
    --CHECK (url regexp 'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)')
);

-----------------
-- Composição
-----------------
CREATE TABLE IF NOT EXISTS tipo_composicao (
    -- Tipo de composição, informa o modo como um artista contribuiu na concepção da música

    -- Identificador único
    id_tipo_composicao int PRIMARY KEY,
    -- Nome
    nome text not null,
    -- Descrição
    descricao text not null
);

CREATE TABLE IF NOT EXISTS artista (
    -- Artista que realizou alguma contribuição na composição de uma música

    -- Identificador único
    id_artista int PRIMARY KEY,
    -- Nome mais comumente utilizado para referenciar o artista
    nome_artistico text not null
);

CREATE TABLE IF NOT EXISTS composicao_musica (
    -- Artista que realizou alguma contribuição na composição de uma música

    id_composicao_musica INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Identificador único
    id_musica int not null CONSTRAINT id_musica REFERENCES musica(id_musica),
    -- Artista que realizou a contribuição.
    -- Null quando é uma adaptação. A adaptação é indicada em `adaptacao`
    id_artista int CONSTRAINT id_artista REFERENCES artista(id_artista),
    -- Forma como se deu a contribuição para a composição.
    -- Pode ser nula no caso em que é um trecho de uma leitura bíblica
    id_tipo_composicao int CONSTRAINT id_tipo_composicao REFERENCES tipo_composicao(id_tipo_composicao),
    -- Texto que informa a adaptação realizada. Ex: Lc: 15:10-15
    adaptacao text
);

-----------------
-- Álbum e faixas
-----------------
CREATE TABLE IF NOT EXISTS album (
    -- Álbum de músicas, geralmente em Compact-Disk (CD), em Vinil, ou em uma fita K7
    id_album INTEGER PRIMARY KEY AUTOINCREMENT,

    nome text not null
);

CREATE TABLE IF NOT EXISTS faixa (
    -- Álbum de músicas, geralmente em Compact-Disk (CD), em Vinil, ou em uma fita K7
    id_faixa INTEGER PRIMARY KEY AUTOINCREMENT,

    id_album int not null CONSTRAINT id_album REFERENCES album(id_album),
    id_musica int not null CONSTRAINT id_musica REFERENCES musica(id_musica),

    isrc text dafault null,  -- International Standard Recording Code, ou Código de Gravação Padrão Internacional
    numero number default null  -- Número da faixa. Idealmente, toda faixa possui um número, entretanto, algumas são desconhecidas
);