-----------------
-- Música
-----------------
ALTER TABLE musica ADD COLUMN crc32 integer not null default 0;


-----------------
-- Biblioteca
-----------------
-- Biblioteca possui obras
-- Um usuário pode pegar um exemplar das obras
-- Para saber se um exemplar é o mais atual, consulta-se o crc32
-- Caso o exemplar não seja o mais atual, inativa ele e gera um novo registro
CREATE TABLE IF NOT EXISTS exemplar_biblioteca (
    -- Obra registrada na biblioteca
    id_exemplar INTEGER PRIMARY KEY AUTOINCREMENT,
    id_obra INTEGER NOT NULL, -- Chave estrangeira para a obra presente na biblioteca

    titulo text not null, -- Nome do exemplar (snapshot do nome da obra)
    descricao text not null, -- Descrição do exemplar (snapshot da descrição da obra)

    crc32 integer not null, -- Identificador de versão da obra baseado em um checksum
    ativo boolean default true
);