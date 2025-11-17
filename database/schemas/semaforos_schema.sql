CREATE TABLE IF NOT EXISTS semaforos (
    _id INTEGER PRIMARY KEY,
    semaforo INTEGER,
    localizacao1 VARCHAR(255),
    localizacao2 VARCHAR(255),
    bairro VARCHAR(255),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    tipo VARCHAR(255),
    funcionamento VARCHAR(255),
    id_semaforo INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);