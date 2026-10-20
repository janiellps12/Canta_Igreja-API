-----------------
-- Música Busca
-----------------
CREATE VIRTUAL TABLE musica_busca USING fts5 (
    -- Tabela específica para busca de músicas
    titulo, letra,
    content=musica, content_rowid=id_musica
);

--
CREATE TRIGGER musica_insert_trigger AFTER INSERT ON musica BEGIN
  INSERT INTO musica_busca(rowid, titulo, letra) VALUES (new.id_musica, new.titulo, new.letra);
END;
CREATE TRIGGER musica_delete_trigger AFTER DELETE ON musica BEGIN
  INSERT INTO musica_busca(musica_busca, rowid, titulo, letra) VALUES('delete', old.id_musica, old.titulo, old.letra);
END;
CREATE TRIGGER musica_update_trigger AFTER UPDATE ON musica BEGIN
  INSERT INTO musica_busca(musica_busca, rowid, titulo, letra) VALUES('delete', old.id_musica, old.titulo, old.letra);
  INSERT INTO musica_busca(rowid, titulo, letra) VALUES (new.id_musica, new.titulo, new.letra);
END;
