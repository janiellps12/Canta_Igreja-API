-- https://stackoverflow.com/a/70600646
-- Replace "role_dml" with the name of the role you want to grant permissions to.
REVOKE ALL ON DATABASE canta_igreja FROM PUBLIC;
REVOKE CREATE ON SCHEMA public FROM PUBLIC;

GRANT CONNECT ON DATABASE canta_igreja TO role_dml;
GRANT TEMPORARY ON DATABASE canta_igreja TO role_dml;

ALTER DEFAULT PRIVILEGES IN SCHEMA auth
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO role_dml;

ALTER DEFAULT PRIVILEGES IN SCHEMA repertorio
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO role_dml;