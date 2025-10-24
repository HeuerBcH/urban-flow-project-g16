# analise-visualizacao-dados-g17

https://mapsplatform.google.com/lp/maps-apis/
API google maps

https://www.openstreetmap.org/#map=18/-8.064366/-34.878910
Open Street Map

https://openweathermap.org/api
OpenWeather

urbanflow/
├── data/
│   ├── raw/                        # DADOS BRUTOS
│   │   ├── linha_701.csv
│   │   ├── linha_702.csv 
│   │   │   └── ... (16 arquivos)
│   │   └── gtfs/                   # Dados GTFS
│   │   └── complementares/         # Dados auxiliares (metadados, trajetos, etc)
│   ├── samples/                    # AMOSTRAS - Subconjuntos pequenos para teste
│   │   └── amostras_1000_linhas/
│   ├── processed/                  # DADOS PROCESSADOS
│   └── analysis/                   # ANÁLISES - Relatórios, estatísticas, métricas de qualidade
├── scripts/
│   ├── database/                   # SCRIPTS DE BANCO - Setup, migrações, carregamento
│   ├── collectors/                 # COLETORES - APIs
│   └── utils/                      # UTILITÁRIOS - Funções auxiliares reutilizáveis
├── database/
│   ├── schemas/                    # SCHEMAS SQL - Definições de tabelas, índices
│   └── migrations/                 # MIGRAÇÕES - Scripts para evolução do schema
├── grafana/                        # Configurações do Grafana
└── .env.example




scripts/                           # MOTOR DO PROJETO - Todo código executável
│
├── database/                      # CAMADA DE DADOS - Interação com PostgreSQL
│   │
│   ├── setup_database.py          # Configura inicialmente o schema no Neon
│   └── cleaning.ipynb             # Limpa e Carrega os CSVs para o banco
├── collectors/                    # CAMADA DE COLETA - Integração com APIs externas
│   │
│   ├── weather_collector.py       # Coleta dados de clima da API
│   ├── osm_collector.py           # Coleta dados geoespaciais do OpenStreetMap
│   └── sptrans_collector.py       # Coleta dados em tempo real (se disponível)
└── utils/                         # BIBLIOTECA INTERNA - Funções compartilhadas (Código reutilizável)




grafana/                            # CAMADA DE VISUALIZAÇÃO - Dashboards e relatórios
│
├── dashboard.json                 # Export do dashboard principal
├── datasource.yaml                # Configuração da conexão com Neon
└── alerts.yaml                    # Configuração de alertas e notificações
