CREATE SCHEMA IF NOT EXISTS repertorio;

---------------------------
-- Repertório
---------------------------
CREATE TABLE IF NOT EXISTS repertorio.repertorio (
    id SERIAL PRIMARY KEY,
    slug varchar(25) NOT NULL,

    repertorio json,

    estado varchar(25) NOT NULL default 'publico',

    criado_por int REFERENCES auth.conta(id) NOT NULL,

    criado_em timestamp NOT NULL default now(),
	atualizado_em timestamp default NULL
);

CREATE INDEX idx_repertorio_repertorio_slug ON repertorio.repertorio (slug);

comment on table repertorio.repertorio is 'Coletânea de músicas';

comment on column repertorio.repertorio.slug is 'Slug em formato nanoid - 10 caracteres';
comment on column repertorio.repertorio.estado is 'Estado do repertório: publico, privado, excluido';
