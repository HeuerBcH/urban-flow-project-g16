-- 1) Extensão PostGIS (se ainda não existir)
CREATE EXTENSION IF NOT EXISTS postgis;

-- 2) Tabela da Faixa Azul
DROP TABLE IF EXISTS faixaazul;

CREATE TABLE faixaazul (
  id   SERIAL PRIMARY KEY,
  name TEXT,
  tipo TEXT,
  geom geometry(LineString, 4326)  -- CRS84 ~ EPSG:4326
);

-- 3) 
DO $$
DECLARE
  fc jsonb;
BEGIN
  -- Lê o arquivo GeoJSON que você copiou para /tmp
  fc := pg_read_file('/tmp/faixaazul_clean.geojson')::jsonb;

  -- Insere cada feature na tabela faixaazul
  INSERT INTO faixaazul (name, tipo, geom)
  SELECT
    feat->'properties'->>'Name' AS name,
    feat->'properties'->>'Tipo' AS tipo,
    ST_SetSRID(
      ST_GeomFromGeoJSON(feat->>'geometry'),
      4326
    ) AS geom
  FROM jsonb_array_elements(fc->'features') AS feat;
END$$;
