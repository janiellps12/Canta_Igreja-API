-----------------
-- Música
-----------------
ALTER TABLE musica ADD COLUMN contribuidores TEXT not null default '{}';
ALTER TABLE musica ADD COLUMN midias TEXT not null default '{}';
