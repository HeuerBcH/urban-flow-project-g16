#!/usr/bin/env python3
"""
Corrige a tabela fluxo_velocidade_15min: altera minutos_intervalo de INTEGER para VARCHAR
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

def fix_table():
    """Corrige o tipo da coluna minutos_intervalo"""
    print("=" * 60)
    print("Corrigindo tabela fluxo_velocidade_15min")
    print("=" * 60)
    
    try:
        conn = get_db_connection()
        print("✅ Conexão estabelecida\n")
        
        with conn.cursor() as cur:
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'fluxo_velocidade_15min'
                );
            """)
            
            if not cur.fetchone()[0]:
                print("⚠️  Tabela não existe. Criando...")
                base_dir = Path(__file__).parent.parent.parent
                schema_file = base_dir / 'database' / 'schemas' / 'fluxo_velocidade_15min_schema.sql'
                
                with open(schema_file, 'r', encoding='utf-8') as f:
                    schema_sql = f.read()
                cur.execute(schema_sql)
                conn.commit()
                print("✅ Tabela criada com schema corrigido")
            else:
                print("📋 Tabela existe. Alterando tipo da coluna...")
                cur.execute("""
                    ALTER TABLE fluxo_velocidade_15min 
                    ALTER COLUMN minutos_intervalo TYPE VARCHAR(255);
                """)
                conn.commit()
                print("✅ Coluna alterada com sucesso")
        
        conn.close()
        print("\n" + "=" * 60)
        print("✅ Correção concluída!")
        print("=" * 60)
        print("\nAgora você pode rodar: python scripts/database/load_data.py")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    fix_table()

