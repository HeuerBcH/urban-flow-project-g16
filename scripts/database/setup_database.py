#!/usr/bin/env python3
"""
Cria todas as tabelas do banco PostgreSQL definidas nos schemas SQL
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import psycopg2
from psycopg2 import sql

load_dotenv()

def get_db_connection():
    """Cria conexão com PostgreSQL usando DATABASE_URL ou variáveis individuais"""
    database_url = os.getenv('DATABASE_URL')
    
    if database_url:
        return psycopg2.connect(database_url)
    else:
        return psycopg2.connect(
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT', '5432'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )

def execute_schema_file(conn, schema_file_path):
    """Executa um arquivo SQL de schema"""
    try:
        with open(schema_file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        with conn.cursor() as cur:
            cur.execute(sql_content)
            conn.commit()
        
        table_name = schema_file_path.stem
        print(f"✅ Tabela criada/verificada: {table_name}")
        return True
    except Exception as e:
        print(f"❌ Erro ao executar {schema_file_path.name}: {e}")
        conn.rollback()
        return False

def setup_database():
    """Cria todas as tabelas do banco de dados"""
    base_dir = Path(__file__).parent.parent.parent
    schemas_dir = base_dir / 'database' / 'schemas'
    
    schema_files = [
        'equipamentos_medicao_schema.sql',
        'semaforos_schema.sql',
        'monitoramento_cttu_schema.sql',
        'fluxo_veiculos_hora_schema.sql',
        'fluxo_velocidade_15min_schema.sql',
        'relatorio_fluxo_agosto_schema.sql',
        'relatorio_fluxo_fevereiro_schema.sql',
    ]
    
    print("=" * 60)
    print("Configurando banco de dados PostgreSQL")
    print("=" * 60)
    
    try:
        conn = get_db_connection()
        print("✅ Conexão com banco estabelecida\n")
        
        success_count = 0
        for schema_file in schema_files:
            schema_path = schemas_dir / schema_file
            if schema_path.exists():
                if execute_schema_file(conn, schema_path):
                    success_count += 1
            else:
                print(f"⚠️  Arquivo não encontrado: {schema_file}")
        
        conn.close()
        
        print("\n" + "=" * 60)
        print(f"✅ Setup concluído: {success_count}/{len(schema_files)} tabelas configuradas")
        print("=" * 60)
        
    except psycopg2.OperationalError as e:
        print(f"❌ Erro de conexão: {e}")
        print("\nVerifique suas variáveis de ambiente:")
        print("  - DATABASE_URL (formato completo)")
        print("  - Ou DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    setup_database()
