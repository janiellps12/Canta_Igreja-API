-----------------
-- Música
-----------------
-- Rótulos é um json array de strings
--  - Os rótulos serão representados dentro de rotulos como uma lista de string
--  - Quem for consumir a lista, pode - por conta própria - separar os rótulos em categorias
-- ["Entrada", "Batismo", "Primeira Eucaristia"]
ALTER TABLE musica ADD COLUMN rotulos TEXT not null default '[]';
