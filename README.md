# analise-visualizacao-dados-g17

https://mapsplatform.google.com/lp/maps-apis/
API google maps

https://www.openstreetmap.org/#map=18/-8.064366/-34.878910
Open Street Map

https://openweathermap.org/api
OpenWeather

urbanflow/
├── data/
│ ├── raw/ # DADOS BRUTOS
│ │ ├── linha_701.csv
│ │ ├── linha_702.csv
│ │ │ └── ... (16 arquivos)
│ │ └── gtfs/ # Dados GTFS
│ │ └── complementares/ # Dados auxiliares (metadados, trajetos, etc)
│ ├── samples/ # AMOSTRAS - Subconjuntos pequenos para teste
│ │ └── amostras_1000_linhas/
│ ├── processed/ # DADOS PROCESSADOS
│ └── analysis/ # ANÁLISES - Relatórios, estatísticas, métricas de qualidade
├── scripts/
│ ├── database/ # SCRIPTS DE BANCO - Setup, migrações, carregamento
│ ├── collectors/ # COLETORES - APIs
│ └── utils/ # UTILITÁRIOS - Funções auxiliares reutilizáveis
├── database/
│ ├── schemas/ # SCHEMAS SQL - Definições de tabelas, índices
│ └── migrations/ # MIGRAÇÕES - Scripts para evolução do schema
├── grafana/ # Configurações do Grafana
└── .env.example

scripts/ # MOTOR DO PROJETO - Todo código executável
│
├── database/ # CAMADA DE DADOS - Interação com PostgreSQL
│ │
│ ├── setup_database.py # Configura inicialmente o schema no Neon
│ └── cleaning.ipynb # Limpa e Carrega os CSVs para o banco
├── collectors/ # CAMADA DE COLETA - Integração com APIs externas
│ │
│ ├── weather_collector.py # Coleta dados de clima da API
│ ├── osm_collector.py # Coleta dados geoespaciais do OpenStreetMap
│ └── sptrans_collector.py # Coleta dados em tempo real (se disponível)
└── utils/ # BIBLIOTECA INTERNA - Funções compartilhadas (Código reutilizável)

grafana/ # CAMADA DE VISUALIZAÇÃO - Dashboards e relatórios
│
├── dashboard.json # Export do dashboard principal
├── datasource.yaml # Configuração da conexão com Neon
└── alerts.yaml # Configuração de alertas e notificações

## Passo a Passo: Processar Dados e Popular Banco

### 1. Preparar os Dados

Coloque os arquivos CSV brutos em `data/raw/` e os arquivos GTFS (`.txt`) em `data/raw/gtfs/`.

### 2. Processar Dados Normais

```bash
# Executar notebook de limpeza
jupyter notebook scripts/database/cleaning.ipynb
```

Execute todas as células do notebook (Run -> Run All Cells). Isso gera:

- Arquivos processados em `data/processed/`
- Schemas SQL em `database/schemas/`

### 3. Processar Dados GTFS

```bash
python scripts/database/clean_gtfs.py
```

Isso processa os arquivos GTFS e salva em `data/processed/gtfs/`.

### 4. Gerar Arquivos SQL

```bash
python scripts/database/generate_sql_inserts.py
```

Isso gera arquivos SQL completos (CREATE TABLE + INSERT) em `database/sql_complete/`.

### 5. Criar Banco PostgreSQL no Docker

```bash
# Iniciar com docker-compose
docker-compose up -d

# Parar o container
docker-compose down

# Ver logs
docker-compose logs -f postgres
```

### 6. Popular Banco PostgreSQL

**Se você criou o banco no Docker (passo 5), use:**

```bash
# Copiar arquivos SQL para o container
docker cp database/sql_complete/. urbanflow-postgres:/tmp/sql/

# IMPORTANTE: Se você já executou os arquivos antes e quer reprocessar, limpe as tabelas primeiro:
# (Esses comandos ignoram erros se as tabelas não existirem - seguro para primeira execução)

docker exec -i urbanflow-postgres psql -U postgres -d urbanflow -c "TRUNCATE TABLE semaforos CASCADE;" 2>$null
docker exec -i urbanflow-postgres psql -U postgres -d urbanflow -c "TRUNCATE TABLE equipamentos_medicao_velocidade CASCADE;" 2>$null
docker exec -i urbanflow-postgres psql -U postgres -d urbanflow -c "TRUNCATE TABLE fluxo_veiculos_hora CASCADE;" 2>$null
docker exec -i urbanflow-postgres psql -U postgres -d urbanflow -c "TRUNCATE TABLE fluxo_velocidade_15min CASCADE;" 2>$null
docker exec -i urbanflow-postgres psql -U postgres -d urbanflow -c "TRUNCATE TABLE monitoramento_cttu CASCADE;" 2>$null
docker exec -i urbanflow-postgres psql -U postgres -d urbanflow -c "TRUNCATE TABLE relatorio_fluxo_agosto CASCADE;" 2>$null
docker exec -i urbanflow-postgres psql -U postgres -d urbanflow -c "TRUNCATE TABLE relatorio_fluxo_fevereiro CASCADE;" 2>$null

# Limpar tabelas GTFS (se processadas)
docker exec -i urbanflow-postgres psql -U postgres -d urbanflow -c "TRUNCATE TABLE gtfs_agency CASCADE;" 2>$null
docker exec -i urbanflow-postgres psql -U postgres -d urbanflow -c "TRUNCATE TABLE gtfs_calendar CASCADE;" 2>$null
docker exec -i urbanflow-postgres psql -U postgres -d urbanflow -c "TRUNCATE TABLE gtfs_calendar_dates CASCADE;" 2>$null
docker exec -i urbanflow-postgres psql -U postgres -d urbanflow -c "TRUNCATE TABLE gtfs_fare_attributes CASCADE;" 2>$null
docker exec -i urbanflow-postgres psql -U postgres -d urbanflow -c "TRUNCATE TABLE gtfs_fare_rules CASCADE;" 2>$null
docker exec -i urbanflow-postgres psql -U postgres -d urbanflow -c "TRUNCATE TABLE gtfs_feed_info CASCADE;" 2>$null
docker exec -i urbanflow-postgres psql -U postgres -d urbanflow -c "TRUNCATE TABLE gtfs_routes CASCADE;" 2>$null
docker exec -i urbanflow-postgres psql -U postgres -d urbanflow -c "TRUNCATE TABLE gtfs_shapes CASCADE;" 2>$null
docker exec -i urbanflow-postgres psql -U postgres -d urbanflow -c "TRUNCATE TABLE gtfs_stop_times CASCADE;" 2>$null
docker exec -i urbanflow-postgres psql -U postgres -d urbanflow -c "TRUNCATE TABLE gtfs_stops CASCADE;" 2>$null
docker exec -i urbanflow-postgres psql -U postgres -d urbanflow -c "TRUNCATE TABLE gtfs_trips CASCADE;" 2>$null

# Popular banco - Dados normais
docker exec -i urbanflow-postgres psql -U postgres -d urbanflow -f /tmp/sql/semaforos_complete.sql

docker exec -i urbanflow-postgres psql -U postgres -d urbanflow -f /tmp/sql/equipamentos_medicao_velocidade_complete.sql

docker exec -i urbanflow-postgres psql -U postgres -d urbanflow -f /tmp/sql/fluxo_veiculos_hora_complete.sql

docker exec -i urbanflow-postgres psql -U postgres -d urbanflow -f /tmp/sql/fluxo_velocidade_15min_complete.sql

docker exec -i urbanflow-postgres psql -U postgres -d urbanflow -f /tmp/sql/monitoramento_cttu_complete.sql

docker exec -i urbanflow-postgres psql -U postgres -d urbanflow -f /tmp/sql/relatorio_fluxo_agosto_complete.sql

docker exec -i urbanflow-postgres psql -U postgres -d urbanflow -f /tmp/sql/relatorio_fluxo_fevereiro_complete.sql

# Popular banco - Dados GTFS
docker exec -i urbanflow-postgres psql -U postgres -d urbanflow -f /tmp/sql/gtfs_agency_complete.sql

docker exec -i urbanflow-postgres psql -U postgres -d urbanflow -f /tmp/sql/gtfs_calendar_complete.sql

docker exec -i urbanflow-postgres psql -U postgres -d urbanflow -f /tmp/sql/gtfs_calendar_dates_complete.sql

docker exec -i urbanflow-postgres psql -U postgres -d urbanflow -f /tmp/sql/gtfs_fare_attributes_complete.sql

docker exec -i urbanflow-postgres psql -U postgres -d urbanflow -f /tmp/sql/gtfs_fare_rules_complete.sql

docker exec -i urbanflow-postgres psql -U postgres -d urbanflow -f /tmp/sql/gtfs_feed_info_complete.sql

docker exec -i urbanflow-postgres psql -U postgres -d urbanflow -f /tmp/sql/gtfs_routes_complete.sql

docker exec -i urbanflow-postgres psql -U postgres -d urbanflow -f /tmp/sql/gtfs_shapes_complete.sql

docker exec -i urbanflow-postgres psql -U postgres -d urbanflow -f /tmp/sql/gtfs_stop_times_complete.sql

docker exec -i urbanflow-postgres psql -U postgres -d urbanflow -f /tmp/sql/gtfs_stops_complete.sql

docker exec -i urbanflow-postgres psql -U postgres -d urbanflow -f /tmp/sql/gtfs_trips_complete.sql
```

**Se você tem PostgreSQL instalado localmente, use:**

```bash
# Popular banco - Dados normais
psql -U postgres -d urbanflow -f database/sql_complete/semaforos_complete.sql

psql -U postgres -d urbanflow -f database/sql_complete/equipamentos_medicao_velocidade_complete.sql

psql -U postgres -d urbanflow -f database/sql_complete/fluxo_veiculos_hora_complete.sql

psql -U postgres -d urbanflow -f database/sql_complete/fluxo_velocidade_15min_complete.sql

psql -U postgres -d urbanflow -f database/sql_complete/monitoramento_cttu_complete.sql

psql -U postgres -d urbanflow -f database/sql_complete/relatorio_fluxo_agosto_complete.sql

psql -U postgres -d urbanflow -f database/sql_complete/relatorio_fluxo_fevereiro_complete.sql

# Popular banco - Dados GTFS
psql -U postgres -d urbanflow -f database/sql_complete/gtfs_agency_complete.sql

psql -U postgres -d urbanflow -f database/sql_complete/gtfs_calendar_complete.sql

psql -U postgres -d urbanflow -f database/sql_complete/gtfs_calendar_dates_complete.sql

psql -U postgres -d urbanflow -f database/sql_complete/gtfs_fare_attributes_complete.sql

psql -U postgres -d urbanflow -f database/sql_complete/gtfs_fare_rules_complete.sql

psql -U postgres -d urbanflow -f database/sql_complete/gtfs_feed_info_complete.sql

psql -U postgres -d urbanflow -f database/sql_complete/gtfs_routes_complete.sql

psql -U postgres -d urbanflow -f database/sql_complete/gtfs_shapes_complete.sql

psql -U postgres -d urbanflow -f database/sql_complete/gtfs_stop_times_complete.sql

psql -U postgres -d urbanflow -f database/sql_complete/gtfs_stops_complete.sql

psql -U postgres -d urbanflow -f database/sql_complete/gtfs_trips_complete.sql
```

**Ou executar todos de uma vez (Docker):**

```bash
# Windows PowerShell
docker cp database/sql_complete/. urbanflow-postgres:/tmp/sql/
Get-ChildItem database/sql_complete/*.sql | ForEach-Object {
    $fileName = $_.Name
    docker exec -i urbanflow-postgres psql -U postgres -d urbanflow -f /tmp/sql/$fileName
}

# Linux/Mac
docker cp database/sql_complete/. urbanflow-postgres:/tmp/sql/
for file in database/sql_complete/*.sql; do
    docker exec -i urbanflow-postgres psql -U postgres -d urbanflow -f /tmp/sql/$(basename "$file")
done
```
