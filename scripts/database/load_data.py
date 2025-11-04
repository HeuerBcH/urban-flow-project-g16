#!/usr/bin/env python3
"""
Carrega dados dos CSVs processados no banco PostgreSQL
"""

import os
import sys
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import execute_values
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

def get_table_columns(conn, table_name):
    """Obtém as colunas da tabela no banco"""
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = %s
                ORDER BY ordinal_position;
            """, (table_name,))
            return [row[0] for row in cur.fetchall()]
    except Exception as e:
        print(f"   ⚠️  Erro ao obter colunas da tabela: {e}")
        return None

def load_csv_to_table(conn, csv_path, table_name):
    """Carrega um CSV na tabela correspondente"""
    try:
        print(f"\n📂 Carregando {csv_path.name}...")
        
        df = pd.read_csv(csv_path, encoding='utf-8')
        
        if df.empty:
            print(f"⚠️  Arquivo vazio: {csv_path.name}")
            return False
        
        print(f"   📊 {len(df)} linhas encontradas")
        
        # Remove colunas duplicadas
        df = df.loc[:, ~df.columns.duplicated()]
        
        # Valida colunas: apenas as que existem tanto no CSV quanto na tabela
        table_columns = get_table_columns(conn, table_name)
        if table_columns is None:
            return False
        
        table_columns_filtered = [col for col in table_columns if col != 'created_at']
        valid_columns = [col for col in df.columns if col in table_columns_filtered]
        
        if not valid_columns:
            print(f"⚠️  Nenhuma coluna válida encontrada (CSV e tabela não correspondem)")
            print(f"   Colunas no CSV: {list(df.columns)}")
            print(f"   Colunas na tabela: {table_columns_filtered}")
            return False
        
        df = df[valid_columns]
        df = df.dropna(how='all')
        df = df.where(pd.notnull(df), None)  # Converte NaN para None (NULL no SQL)
        
        if len(df) == 0:
            print(f"⚠️  Nenhuma linha válida após limpeza")
            return False
        
        values = [tuple(row) for row in df[valid_columns].values]
        
        # execute_values precisa de query com UM único %s - substitui por múltiplos VALUES
        # sql.Identifier previne SQL injection e escapa nomes corretamente
        columns_identifiers = sql.SQL(', ').join(map(sql.Identifier, valid_columns))
        insert_query_template = sql.SQL(
            "INSERT INTO {} ({}) VALUES %s"
        ).format(
            sql.Identifier(table_name),
            columns_identifiers
        )
        insert_query_str = insert_query_template.as_string(conn)
        
        with conn.cursor() as cur:
            # Limpa tabela antes de inserir (comentar para manter dados existentes)
            cur.execute(sql.SQL("TRUNCATE TABLE {} CASCADE").format(sql.Identifier(table_name)))
            
            # Insere em lotes de 1000 registros para melhor performance
            execute_values(
                cur,
                insert_query_str,
                values,
                page_size=1000
            )
            conn.commit()
        
        print(f"✅ {len(values)} linhas inseridas em {table_name}")
        print(f"   📋 Colunas: {', '.join(valid_columns)}")
        return True
        
    except FileNotFoundError:
        print(f"❌ Arquivo não encontrado: {csv_path}")
        return False
    except pd.errors.EmptyDataError:
        print(f"⚠️  Arquivo vazio: {csv_path.name}")
        return False
    except Exception as e:
        print(f"❌ Erro ao carregar {csv_path.name}: {e}")
        conn.rollback()
        return False

def load_all_data():
    """Carrega todos os CSVs processados no banco"""
    base_dir = Path(__file__).parent.parent.parent
    processed_dir = base_dir / 'data' / 'processed'
    
    csv_to_table = {
        'equipamentos_medicao_velocidade_clean.csv': 'equipamentos_medicao_velocidade',
        'semaforos_clean.csv': 'semaforos',
        'monitoramento_cttu_clean.csv': 'monitoramento_cttu',
        'fluxo_veiculos_hora_clean.csv': 'fluxo_veiculos_hora',
        'fluxo_velocidade_15min_clean.csv': 'fluxo_velocidade_15min',
        'relatorio_fluxo_agosto_2025_clean.csv': 'relatorio_fluxo_agosto',
        'relatorio_fluxo_fevereiro_2025_clean.csv': 'relatorio_fluxo_fevereiro',
    }
    
    print("=" * 60)
    print("Carregando dados no banco PostgreSQL")
    print("=" * 60)
    
    try:
        conn = get_db_connection()
        print("✅ Conexão com banco estabelecida\n")
        
        success_count = 0
        total_files = len(csv_to_table)
        
        for csv_file, table_name in csv_to_table.items():
            csv_path = processed_dir / csv_file
            if csv_path.exists():
                if load_csv_to_table(conn, csv_path, table_name):
                    success_count += 1
            else:
                print(f"⚠️  Arquivo não encontrado: {csv_file}")
        
        conn.close()
        
        print("\n" + "=" * 60)
        print(f"✅ Carregamento concluído: {success_count}/{total_files} arquivos carregados")
        print("=" * 60)
        
    except psycopg2.OperationalError as e:
        print(f"❌ Erro de conexão: {e}")
        print("\nVerifique suas variáveis de ambiente:")
        print("  - DATABASE_URL (formato completo)")
        print("  - Ou DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    load_all_data()

