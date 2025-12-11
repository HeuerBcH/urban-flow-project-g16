CREATE TABLE IF NOT EXISTS monitoramento_cttu (
    nome VARCHAR(255),
    endereco VARCHAR(255),
    longitude DECIMAL(11, 8),
    latitude DECIMAL(10, 8),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);