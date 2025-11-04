#!/usr/bin/env python3
"""
Testa conexão com o banco PostgreSQL
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import psycopg2

load_dotenv()

def test_connection():
    """Testa conexão com PostgreSQL usando DATABASE_URL ou variáveis individuais"""
    print("=" * 60)
    print("Testando conexão com PostgreSQL")
    print("=" * 60)
    
    try:
        database_url = os.getenv('DATABASE_URL')
        
        if database_url:
            print("📡 Usando DATABASE_URL...")
            conn = psycopg2.connect(database_url)
        else:
            print("📡 Usando variáveis individuais...")
            conn = psycopg2.connect(
                host=os.getenv('DB_HOST'),
                port=os.getenv('DB_PORT', '5432'),
                database=os.getenv('DB_NAME'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD')
            )
        
        with conn.cursor() as cur:
            cur.execute("SELECT version();")
            version = cur.fetchone()[0]
            
            cur.execute("SELECT current_database();")
            db_name = cur.fetchone()[0]
            
            cur.execute("SELECT current_user;")
            user = cur.fetchone()[0]
        
        conn.close()
        
        print("\n✅ Conexão estabelecida com sucesso!")
        print(f"   📊 Banco: {db_name}")
        print(f"   👤 Usuário: {user}")
        print(f"   🔧 PostgreSQL: {version.split(',')[0]}")
        print("\n" + "=" * 60)
        return True
        
    except psycopg2.OperationalError as e:
        print(f"\n❌ Erro de conexão: {e}")
        print("\nVerifique suas variáveis de ambiente:")
        print("  - DATABASE_URL (formato: postgresql://user:pass@host:port/db)")
        print("  - Ou configure: DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD")
        print("\nCertifique-se de criar um arquivo .env na raiz do projeto.")
        return False
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
