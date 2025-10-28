CREATE TABLE IF NOT EXISTS equipamentos_medicao_velocidade (
    _id INTEGER PRIMARY KEY,
    equipamento VARCHAR(255),
    tipo VARCHAR(255),
    logradouro VARCHAR(255),
    velocidade_via VARCHAR(255),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);