CREATE SCHEMA IF NOT EXISTS auth;

---------------------------
-- Conta
---------------------------
CREATE TABLE IF NOT EXISTS auth.conta (
    id SERIAL PRIMARY KEY,

    slug varchar(25) NOT NULL,
    email varchar NOT NULL UNIQUE,

    nome varchar(300) NOT NULL,

    subject varchar NOT NULL,
    provider varchar NOT NULL default 'google_api',

    criado_em timestamp NOT NULL default now()
);

CREATE INDEX idx_auth_conta_slug ON auth.conta (slug);
CREATE INDEX idx_auth_conta_subject ON auth.conta (subject);

comment on table auth.conta is 'Conta de usuário';

comment on column auth.conta.slug is 'Slug em formato nanoid - 10 caracteres';
comment on column auth.conta.nome is 'Nome da pessoa associada a conta';
comment on column auth.conta.subject is 'Subject jwt - Identificador único considerando a forma de autenticação (provider)';
comment on column auth.conta.provider is 'Provedor da forma de autenticação';
