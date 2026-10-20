CREATE TABLE IF NOT EXISTS sugestao_repertorio (
    id_sugestao_repertorio INTEGER PRIMARY KEY,
    id_romcal TEXT DEFAULT NULL,
    ano_liturgico TEXT DEFAULT NULL,
    titulo TEXT NOT NULL,
    resumo TEXT DEFAULT NULL,
    itens TEXT NOT NULL DEFAULT '[]',
    metadata TEXT DEFAULT '{}',
    crc32 INTEGER NOT NULL,
    
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    atualizado_em DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sugestao_repertorio_id_romcal_ano_liturgico
    ON sugestao_repertorio (id_romcal, ano_liturgico);
