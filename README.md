# 🚦 Urban Flow - Sistema de Análise de Mobilidade Urbana

[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)](https://www.postgresql.org/)
[![PostGIS](https://img.shields.io/badge/PostGIS-3.4-green.svg)](https://postgis.net/)
[![Python](https://img.shields.io/badge/Python-3.8+-yellow.svg)](https://www.python.org/)
[![Grafana](https://img.shields.io/badge/Grafana-Latest-orange.svg)](https://grafana.com/)

Sistema completo de análise e visualização de dados de mobilidade urbana, integrando dados de tráfego, transporte público (GTFS), semáforos e infraestrutura viária com visualizações interativas em Grafana.

## 🎯 Sobre o Projeto

O **Urban Flow** é uma plataforma de análise de dados de mobilidade urbana desenvolvida para processar, armazenar e visualizar informações sobre:

- 🚗 Fluxo de veículos e velocidade média
- 🚦 Localização e status de semáforos
- 🚌 Dados de transporte público (formato GTFS)
- 📊 Equipamentos de medição de velocidade
- 🗺️ Dados geoespaciais de infraestrutura viária
- 📈 Relatórios mensais de tráfego

O sistema utiliza PostgreSQL com extensão PostGIS para armazenamento de dados geoespaciais e Grafana para criação de dashboards interativos.

## ✨ Funcionalidades

- **Processamento de Dados**: Pipeline completo de ETL para dados de mobilidade urbana
- **Armazenamento Geoespacial**: Banco de dados PostgreSQL/PostGIS otimizado para consultas espaciais
- **Visualização Interativa**: Dashboards em Grafana com mapas e gráficos em tempo real
- **Suporte GTFS**: Importação e análise de dados de transporte público no formato GTFS
- **Análise Temporal**: Agregações por hora, dia, semana e mês
- **Integração com APIs**: Coleta de dados de clima (OpenWeather) e mapas (OpenStreetMap)

## 🏗️ Arquitetura

```
┌─────────────────┐
│   Dados Brutos  │
│  (CSV, GTFS)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Scripts Python │
│  (Limpeza/ETL)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   PostgreSQL    │
│   + PostGIS     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     Grafana     │
│   (Dashboards)  │
└─────────────────┘
```

## 📦 Pré-requisitos

### Software Necessário

- **Python 3.8+** - [Download](https://www.python.org/downloads/)
- **Docker & Docker Compose** - [Download](https://www.docker.com/products/docker-desktop/)
- **Git** - [Download](https://git-scm.com/downloads)
- **Jupyter Notebook** (incluído nas dependências Python)

## 🚀 Instalação

### 1. Clonar o Repositório

```bash
git clone https://github.com/HeuerBcH/urban-flow-project-g16.git
cd urban-flow-project-g16
```

### 2. Configurar Ambiente Python

```bash
# Criar ambiente virtual (recomendado)
python -m venv venv

# Ativar ambiente virtual
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### 3. Configurar Variáveis de Ambiente

Copie o arquivo `.env.example` para `.env` e configure as variáveis:

```bash
# Windows
copy .env.example .env
# Linux/Mac
cp .env.example .env
```

Edite o arquivo `.env` com suas configurações:

```env
# Configurações do PostgreSQL
POSTGRES_DB=urbanflow
POSTGRES_USER=postgres
POSTGRES_PASSWORD=sua_senha_segura
DB_PORT=5432

# Configurações do Grafana (opcional)
GRAFANA_PDC_TOKEN=seu_token
GRAFANA_PDC_CLUSTER=seu_cluster
GRAFANA_PDC_ID=seu_id
GRAFANA_HOST=http://localhost:3000
```

### 4. Iniciar Serviços com Docker

```bash
# Iniciar PostgreSQL e Grafana Agent
docker-compose up -d

# Verificar se os containers estão rodando
docker ps

# Ver logs em tempo real
docker-compose logs -f
```

## 📁 Estrutura do Projeto

```
urban-flow-project-g16/
│
├── data/                           # Diretório de dados
│   ├── raw/                        # Dados brutos (CSV, GTFS)
│   │   ├── gtfs/                   # Arquivos GTFS (.txt)
│   │   └── complementares/         # Dados auxiliares
│   ├── samples/                    # Amostras para testes
│   │   └── amostras_1000_linhas/
│   ├── processed/                  # Dados processados e limpos
│   └── analysis/                   # Análises e relatórios
│
├── scripts/                        # Scripts Python
│   ├── database/                   # Scripts de banco de dados
│   │   ├── setup_database.py      # Configuração inicial
│   │   ├── cleaning.ipynb          # Notebook de limpeza
│   │   ├── clean_gtfs.py           # Processamento GTFS
│   │   └── generate_sql_inserts.py # Geração de SQL
│   ├── collectors/                 # Coletores de APIs
│   │   ├── weather_collector.py   # API OpenWeather
│   │   ├── osm_collector.py        # OpenStreetMap
│   │   └── sptrans_collector.py    # Dados SPTrans
│   └── utils/                      # Utilitários
│       └── teste_conexao.py        # Teste de conexão DB
│
├── database/                       # Arquivos de banco de dados
│   ├── schemas/                    # Schemas SQL
│   │   ├── semaforos_schema.sql
│   │   ├── fluxo_veiculos_hora_schema.sql
│   │   ├── gtfs_*.sql              # Schemas GTFS
│   │   └── ...
│   ├── migrations/                 # Scripts de migração
│   └── sql_complete/               # SQL completo (CREATE + INSERT)
│
├── grafana/                        # Configurações Grafana
│   ├── dashboard.json              # Dashboard principal
│   └── datasource.yaml             # Configuração de datasource
│
├── docker-compose.yml              # Configuração Docker
├── requirements.txt                # Dependências Python
├── .env.example                    # Exemplo de variáveis de ambiente
├── .gitignore                      # Arquivos ignorados pelo Git
└── README.md                       # Este arquivo
```

## Guia de Uso

### Passo a Passo: Processar Dados e Popular Banco

### 1. Preparar os Dados

**Obter os Dados Brutos**

Os dados brutos necessários para o projeto estão disponíveis no Google Drive:

 🔗 **[Acessar Drive com os Dados](https://drive.google.com/drive/u/1/folders/1HMpYaU5QP3S1Tov7Oe94_EjWSHmJPVJ5)**

Faça o download dos seguintes arquivos:
- Arquivos GTFS (formato `.txt`)
- Scripts SQL prontos (schemas e inserts completos)

> **💡 Dica**: Se você preferir pular as etapas de processamento (passos 2-4), pode baixar diretamente os scripts SQL já processados do Drive e ir direto para o passo 5 (Popular Banco PostgreSQL).

**Organizar os Arquivos**

Após o download, organize os arquivos nas seguintes pastas:

```bash
# Arquivos CSV de tráfego
data/raw/

# Arquivos GTFS (.txt)
data/raw/gtfs/

# Dados complementares (opcional)
data/raw/complementares/
```

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

**Copiar GeoJSON para dentro do container:**

```bash
docker cp data/processed/faixaazul_clean.geojson urbanflow-postgres:/tmp/faixaazul_clean.geojson

# Executar schema GeoJSON
docker exec -i urbanflow-postgres psql -U postgres -d urbanflow -f /database/schemas/geojson_schema.sql
```

### 7. Verificar Dados Carregados

```bash
# Conectar ao banco
docker exec -it urbanflow-postgres psql -U postgres -d urbanflow

# Listar tabelas
\dt

# Verificar quantidade de registros
SELECT 'semaforos' as tabela, COUNT(*) FROM semaforos
UNION ALL
SELECT 'fluxo_veiculos_hora', COUNT(*) FROM fluxo_veiculos_hora
UNION ALL
SELECT 'gtfs_stops', COUNT(*) FROM gtfs_stops;

# Sair
\q
```

## 📊 Dados e Schemas

### Tabelas Principais

#### Dados de Tráfego

- **`semaforos`**: Localização e informações de semáforos
  - Campos: id, logradouro, bairro, latitude, longitude, tipo
  
- **`equipamentos_medicao_velocidade`**: Equipamentos de medição (radares)
  - Campos: id, logradouro, bairro, latitude, longitude, tipo_equipamento
  
- **`fluxo_veiculos_hora`**: Fluxo de veículos agregado por hora
  - Campos: id, data_hora, quantidade_veiculos, velocidade_media, local
  
- **`fluxo_velocidade_15min`**: Fluxo e velocidade em intervalos de 15 minutos
  - Campos: id, timestamp, velocidade_media, volume_trafego, local
  
- **`monitoramento_cttu`**: Dados de monitoramento da CTTU
  - Campos: id, data_hora, tipo_evento, localizacao, descricao

#### Relatórios Mensais

- **`relatorio_fluxo_janeiro`** até **`relatorio_fluxo_agosto`**
  - Dados agregados mensais de fluxo de veículos
  - Campos: data, hora, local, quantidade, velocidade_media

#### Dados GTFS (Transporte Público)

- **`gtfs_agency`**: Informações das agências de transporte
- **`gtfs_routes`**: Rotas de ônibus
- **`gtfs_trips`**: Viagens programadas
- **`gtfs_stops`**: Pontos de parada
- **`gtfs_stop_times`**: Horários de parada
- **`gtfs_shapes`**: Geometria das rotas
- **`gtfs_calendar`**: Calendário de operação
- **`gtfs_calendar_dates`**: Exceções de calendário
- **`gtfs_fare_attributes`**: Atributos de tarifa
- **`gtfs_fare_rules`**: Regras de tarifa
- **`gtfs_feed_info`**: Informações do feed

### Formato GTFS

O projeto suporta o formato [General Transit Feed Specification (GTFS)](https://gtfs.org/), padrão internacional para dados de transporte público. Os arquivos GTFS devem ser colocados no diretório `data/raw/gtfs/`.

## 📈 Visualização com Grafana

### Acessar Grafana

1. Acesse `http://localhost:3000` no navegador
2. Login padrão: `admin` / `admin`
3. Configure o datasource PostgreSQL:
   - Host: `urbanflow-postgres:5432`
   - Database: `urbanflow`
   - User: `postgres`
   - Password: (conforme configurado no `.env`)

### Importar Dashboard

```bash
# O dashboard está em grafana/dashboard.json
# No Grafana:
# 1. Vá em Dashboards > Import
# 2. Faça upload do arquivo grafana/dashboard.json
# 3. Selecione o datasource PostgreSQL configurado
```

## 🐛 Troubleshooting

### Erro: "Container já existe"

```bash
docker rm urbanflow-postgres
docker-compose up -d
```

### Erro: "Porta 5432 já em uso"

```bash
# Alterar porta no .env
DB_PORT=5433

# Ou parar PostgreSQL local
# Windows
net stop postgresql-x64-15
# Linux
sudo systemctl stop postgresql
```

### Erro: "Módulo não encontrado"

```bash
# Reinstalar dependências
pip install -r requirements.txt
```

### Dados não aparecem no Grafana

1. Verificar se o banco tem dados: `SELECT COUNT(*) FROM semaforos;`
2. Verificar conexão do datasource no Grafana
3. Verificar queries nos painéis do dashboard

## 👥 Equipe

**Grupo 16** - Análise e Visualização de Dados de Mobilidade Urbana

### Contribuintes

- Acioli, Erick
- Cardozo, Guilherme
- Fittipaldi, Silvio
- Heuer, Bernardo
- Nunes, Rodrigo
- Perylo, Luis Felipe
- Roma, Eduardo
