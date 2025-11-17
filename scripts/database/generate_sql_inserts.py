#!/usr/bin/env python3
"""
Script para gerar arquivos SQL com INSERT statements a partir dos CSVs processados.
Gera arquivos .sql para popular um banco de dados local PostgreSQL.

Funciona tanto para CSVs normais quanto para GTFS.
"""

import os
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Optional, Tuple


def detect_project_root() -> str:
    """Detecta o diretório raiz do projeto"""
    current_dir = os.getcwd()
    project_root = current_dir
    
    # Procurar pelo diretório que contém o README.md
    while project_root != os.path.dirname(project_root):
        if os.path.exists(os.path.join(project_root, "README.md")):
            break
        project_root = os.path.dirname(project_root)
    
    # Se não encontrou, usar o diretório atual e subir 2 níveis (scripts/database -> scripts -> projeto)
    if not os.path.exists(os.path.join(project_root, "README.md")):
        project_root = os.path.dirname(os.path.dirname(current_dir))
    
    return project_root


def escape_sql_value(value: any, col_type: str = None, col_name: str = None) -> str:
    """Escapa valores para SQL"""
    if pd.isna(value) or value is None:
        return "NULL"
    
    # Converter para string se necessário
    if isinstance(value, (np.integer, np.floating)):
        value = value.item()
    
    # Tratar diferentes tipos
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    
    # Se for uma coluna de telefone, email ou URL, sempre tratar como string
    if col_name and ('phone' in col_name.lower() or 'email' in col_name.lower() or 'url' in col_name.lower()):
        value_str = str(value).replace("'", "''")
        return f"'{value_str}'"
    
    # Se o tipo da coluna é VARCHAR ou TEXT, tratar como string mesmo que seja numérico
    if col_type and ('VARCHAR' in col_type.upper() or 'TEXT' in col_type.upper()):
        # Mas se for um número pequeno e não for telefone/email/url, pode ser um ID numérico válido
        if isinstance(value, (int, float)) and value < 2147483647:  # Limite do INTEGER
            # Verificar se é realmente um número (não um telefone)
            if col_name and 'phone' not in col_name.lower() and 'id' in col_name.lower():
                return str(value)
        # Caso contrário, tratar como string
        value_str = str(value).replace("'", "''")
        return f"'{value_str}'"
    
    if isinstance(value, (int, float)):
        return str(value)
    
    if isinstance(value, pd.Timestamp):
        # Formatar timestamp para SQL
        if col_type == "DATE":
            return f"'{value.strftime('%Y-%m-%d')}'"
        elif col_type == "TIME":
            return f"'{value.strftime('%H:%M:%S')}'"
        else:
            return f"'{value.strftime('%Y-%m-%d %H:%M:%S')}'"
    
    # Strings - escapar aspas simples
    value_str = str(value).replace("'", "''")
    return f"'{value_str}'"


def parse_schema_file(schema_path: str) -> Tuple[str, Dict[str, str]]:
    """Lê um arquivo schema SQL e retorna nome da tabela e mapeamento de colunas para tipos"""
    table_name = None
    columns = {}
    
    try:
        with open(schema_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extrair nome da tabela
        if "CREATE TABLE" in content:
            # Procurar por CREATE TABLE IF NOT EXISTS table_name ou CREATE TABLE table_name
            import re
            match = re.search(r'CREATE TABLE (?:IF NOT EXISTS )?(\w+)', content, re.IGNORECASE)
            if match:
                table_name = match.group(1)
        
        # Extrair colunas e tipos
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('--') or not line or line.startswith('CREATE') or line.startswith(')'):
                continue
            
            # Remover vírgula final
            if line.endswith(','):
                line = line[:-1]
            
            # Parsear coluna e tipo (formato: "coluna TYPE" ou "coluna TYPE PRIMARY KEY")
            parts = line.split()
            if len(parts) >= 2:
                col_name = parts[0].strip()
                col_type = parts[1].strip().upper()
                
                # Remover PRIMARY KEY, SERIAL, etc. do tipo
                if 'PRIMARY' in col_type:
                    continue  # Pular colunas PRIMARY KEY (geralmente são auto-increment)
                
                # Normalizar tipos
                if 'VARCHAR' in col_type or 'TEXT' in col_type:
                    col_type = 'TEXT'
                elif 'INTEGER' in col_type or 'INT' in col_type:
                    col_type = 'INTEGER'
                elif 'DECIMAL' in col_type or 'NUMERIC' in col_type or 'FLOAT' in col_type or 'REAL' in col_type:
                    col_type = 'DECIMAL'
                elif 'DATE' in col_type:
                    col_type = 'DATE'
                elif 'TIME' in col_type:
                    col_type = 'TIME'
                elif 'TIMESTAMP' in col_type:
                    col_type = 'TIMESTAMP'
                elif 'BOOLEAN' in col_type or 'BOOL' in col_type:
                    col_type = 'BOOLEAN'
                
                columns[col_name] = col_type
        
        # Remover created_at se existir (será gerado automaticamente)
        if 'created_at' in columns:
            del columns['created_at']
            
    except Exception as e:
        print(f"[ERRO] Erro ao ler schema {schema_path}: {e}")
    
    return table_name, columns


def find_matching_schema(csv_filename: str, schemas_dir: str) -> Optional[str]:
    """Encontra o arquivo schema correspondente a um CSV"""
    # Mapear nomes de CSV para nomes de schema
    csv_to_schema = {
        "semaforos_clean.csv": "semaforos_schema.sql",
        "equipamentos_medicao_velocidade_clean.csv": "equipamentos_medicao_schema.sql",
        "fluxo_veiculos_hora_clean.csv": "fluxo_veiculos_hora_schema.sql",
        "fluxo_velocidade_15min_clean.csv": "fluxo_velocidade_15min_schema.sql",
        "monitoramento_cttu_clean.csv": "monitoramento_cttu_schema.sql",
        "relatorio_fluxo_janeiro_2025_clean.csv": "relatorio_fluxo_janeiro_schema.sql",
        "relatorio_fluxo_fevereiro_2025_clean.csv": "relatorio_fluxo_fevereiro_schema.sql",
        "relatorio_fluxo_marco_2025_clean.csv": "relatorio_fluxo_marco_schema.sql",
        "relatorio_fluxo_abril_2025_clean.csv": "relatorio_fluxo_abril_schema.sql",
        "relatorio_fluxo_maio_2025_clean.csv": "relatorio_fluxo_maio_schema.sql",
        "relatorio_fluxo_junho_2025_clean.csv": "relatorio_fluxo_junho_schema.sql",
        "relatorio_fluxo_julho_2025_clean.csv": "relatorio_fluxo_julho_schema.sql",
        "relatorio_fluxo_agosto_2025_clean.csv": "relatorio_fluxo_agosto_schema.sql",
    }
    
    # Tentar mapeamento direto
    if csv_filename in csv_to_schema:
        schema_path = os.path.join(schemas_dir, csv_to_schema[csv_filename])
        if os.path.exists(schema_path):
            return schema_path
    
    # Tentar encontrar por padrão (nome do CSV sem _clean.csv + _schema.sql)
    base_name = csv_filename.replace("_clean.csv", "").replace(".csv", "")
    
    # Procurar arquivos schema que correspondam
    if os.path.exists(schemas_dir):
        for schema_file in os.listdir(schemas_dir):
            if schema_file.endswith("_schema.sql"):
                schema_base = schema_file.replace("_schema.sql", "")
                # Verificar se há correspondência parcial
                if base_name in schema_base or schema_base in base_name:
                    schema_path = os.path.join(schemas_dir, schema_file)
                    if os.path.exists(schema_path):
                        return schema_path
    
    return None


def generate_sql_schema_from_df(df: pd.DataFrame, table_name: str, primary_key: Optional[str] = None) -> str:
    """Gera schema SQL automaticamente baseado no DataFrame"""
    if df is None or df.empty:
        return ""
    
    schema_lines = [f"CREATE TABLE IF NOT EXISTS {table_name} ("]
    
    # Adicionar colunas
    for i, (col, dtype) in enumerate(df.dtypes.items()):
        # Converter tipos do pandas para SQL
        if dtype == 'int64':
            sql_type = "INTEGER"
        elif dtype == 'float64':
            sql_type = "DECIMAL(10, 2)"
        elif dtype == 'object':
            # Para strings, verificar tamanho máximo
            try:
                max_len = df[col].astype(str).str.len().max()
                if pd.isna(max_len) or max_len > 255:
                    sql_type = "TEXT"
                else:
                    sql_type = f"VARCHAR({max(255, int(max_len))})"
            except:
                sql_type = "TEXT"
        elif 'datetime' in str(dtype):
            sql_type = "TIMESTAMP"
        else:
            sql_type = "TEXT"
        
        # Correções específicas para tipos de dados GTFS
        # Coordenadas com precisão correta
        if col in ['stop_lat', 'stop_lon', 'shape_pt_lat', 'shape_pt_lon']:
            sql_type = "DECIMAL(10, 8)"
        
        # Horários GTFS: usar VARCHAR porque GTFS permite horas >= 24 (ex: 24:00:05)
        # No GTFS, horas >= 24 representam o dia seguinte
        if col in ['arrival_time', 'departure_time']:
            sql_type = "VARCHAR(10)"  # Formato HH:MM:SS ou HH:MM:SS para horas >= 24
        
        # Datas como DATE em vez de TIMESTAMP
        if col in ['start_date', 'end_date', 'date']:
            sql_type = "DATE"
        
        # Telefones, emails e URLs sempre como VARCHAR/TEXT (mesmo que sejam numéricos)
        if 'phone' in col.lower() or 'email' in col.lower() or 'url' in col.lower():
            sql_type = "VARCHAR(255)"
        
        # Adicionar PRIMARY KEY se especificado
        if primary_key and col == primary_key:
            sql_type += " PRIMARY KEY"
        elif not primary_key:
            # Para GTFS trips, a PRIMARY KEY é trip_id (não route_id que vem antes)
            if 'trips' in table_name.lower() and col == 'trip_id':
                sql_type += " PRIMARY KEY"
            # Para outras tabelas GTFS, geralmente a primeira coluna é um ID
            # MAS calendar_dates precisa de PRIMARY KEY composta (service_id, date)
            elif i == 0 and 'id' in col.lower() and 'calendar_dates' not in table_name.lower() and 'trips' not in table_name.lower():
                sql_type += " PRIMARY KEY"
        
        col_name = col.replace('-', '_')
        schema_lines.append(f"    {col_name} {sql_type},")
    
    # Adicionar campo created_at
    schema_lines.append("    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    
    # PRIMARY KEY composta para tabelas GTFS específicas
    # calendar_dates: (service_id, date) - mesmo service_id pode ter múltiplas datas
    # fare_rules: (fare_id, route_id) - mesmo fare_id pode ter múltiplos route_id
    # shapes: (shape_id, shape_pt_sequence) - mesmo shape_id tem múltiplos pontos
    # stop_times: (trip_id, stop_sequence) - mesmo trip_id tem múltiplas paradas
    # trips: PRIMARY KEY é trip_id (não route_id, que pode ter múltiplas viagens)
    if 'trips' in table_name.lower():
        # Remover PRIMARY KEY de route_id se existir (se foi colocado por engano)
        new_schema_lines = []
        for line in schema_lines:
            if "route_id" in line and "PRIMARY KEY" in line:
                new_line = line.replace(" PRIMARY KEY", "")
                new_schema_lines.append(new_line)
            else:
                new_schema_lines.append(line)
        schema_lines = new_schema_lines
        
        # Garantir que trip_id tem PRIMARY KEY (se não tiver, adicionar)
        trip_id_has_pk = any("trip_id" in line and "PRIMARY KEY" in line for line in schema_lines)
        if not trip_id_has_pk:
            # Encontrar linha com trip_id e adicionar PRIMARY KEY
            for i, line in enumerate(schema_lines):
                if "trip_id" in line and "PRIMARY KEY" not in line:
                    schema_lines[i] = line.replace("trip_id", "trip_id").replace("VARCHAR(255),", "VARCHAR(255) PRIMARY KEY,")
                    break
    
    elif 'calendar_dates' in table_name.lower():
        # Remover PRIMARY KEY de service_id se existir
        new_schema_lines = []
        for line in schema_lines:
            if "service_id" in line and "PRIMARY KEY" in line:
                new_line = line.replace(" PRIMARY KEY", "")
                new_schema_lines.append(new_line)
            else:
                new_schema_lines.append(line)
        schema_lines = new_schema_lines
        
        # Adicionar PRIMARY KEY composta antes do created_at
        for i, line in enumerate(schema_lines):
            if "created_at" in line:
                schema_lines.insert(i, "    PRIMARY KEY (service_id, date),")
                break
    
    elif 'fare_rules' in table_name.lower():
        # Remover PRIMARY KEY de fare_id se existir
        new_schema_lines = []
        for line in schema_lines:
            if "fare_id" in line and "PRIMARY KEY" in line:
                new_line = line.replace(" PRIMARY KEY", "")
                new_schema_lines.append(new_line)
            else:
                new_schema_lines.append(line)
        schema_lines = new_schema_lines
        
        # Adicionar PRIMARY KEY composta antes do created_at
        for i, line in enumerate(schema_lines):
            if "created_at" in line:
                schema_lines.insert(i, "    PRIMARY KEY (fare_id, route_id),")
                break
    
    elif 'shapes' in table_name.lower():
        # Remover PRIMARY KEY de shape_id se existir
        new_schema_lines = []
        for line in schema_lines:
            if "shape_id" in line and "PRIMARY KEY" in line:
                new_line = line.replace(" PRIMARY KEY", "")
                new_schema_lines.append(new_line)
            else:
                new_schema_lines.append(line)
        schema_lines = new_schema_lines
        
        # Adicionar PRIMARY KEY composta antes do created_at
        for i, line in enumerate(schema_lines):
            if "created_at" in line:
                schema_lines.insert(i, "    PRIMARY KEY (shape_id, shape_pt_sequence),")
                break
    
    elif 'stop_times' in table_name.lower():
        # Remover PRIMARY KEY de trip_id se existir
        new_schema_lines = []
        for line in schema_lines:
            if "trip_id" in line and "PRIMARY KEY" in line:
                new_line = line.replace(" PRIMARY KEY", "")
                new_schema_lines.append(new_line)
            else:
                new_schema_lines.append(line)
        schema_lines = new_schema_lines
        
        # Adicionar PRIMARY KEY composta antes do created_at
        for i, line in enumerate(schema_lines):
            if "created_at" in line:
                schema_lines.insert(i, "    PRIMARY KEY (trip_id, stop_sequence),")
                break
    
    schema_lines.append(");")
    
    return "\n".join(schema_lines)


def generate_sql_inserts_content(csv_path: str, schema_path: Optional[str], 
                                  batch_size: int = 1000) -> Tuple[Optional[str], Optional[str], Optional[str], int]:
    """Gera conteúdo SQL com INSERT statements a partir de um CSV. Retorna (table_name, insert_content, schema_content, num_records)"""
    try:
        # Carregar CSV
        print(f"[INFO] Carregando CSV: {os.path.basename(csv_path)}")
        df = pd.read_csv(csv_path, encoding='utf-8')
        print(f"[OK] CSV carregado: {df.shape[0]} registros, {df.shape[1]} colunas")
        
        # Ler schema se disponível
        table_name = None
        column_types = {}
        
        if schema_path and os.path.exists(schema_path):
            print(f"[INFO] Lendo schema: {os.path.basename(schema_path)}")
            table_name, column_types = parse_schema_file(schema_path)
            print(f"[OK] Schema lido: tabela '{table_name}', {len(column_types)} colunas")
        else:
            # Se não houver schema, usar nome do arquivo como tabela
            table_name = os.path.basename(csv_path).replace("_clean.csv", "").replace(".csv", "")
            table_name = table_name.replace("-", "_")
            print(f"[AVISO] Schema não encontrado, usando nome de tabela: {table_name}")
        
        if not table_name:
            print(f"[ERRO] Não foi possível determinar o nome da tabela")
            return None, None, None, 0
        
        # Normalizar nomes de colunas (remover hífens, garantir compatibilidade)
        df.columns = [col.replace('-', '_') for col in df.columns]
        
        # Gerar schema automaticamente se não houver schema_path
        schema_content = None
        if not schema_path:
            print(f"[INFO] Gerando schema automaticamente para {table_name}")
            schema_content = generate_sql_schema_from_df(df, table_name)
            print(f"[OK] Schema gerado automaticamente")
        
        # Remover colunas que não estão no schema (se schema existir)
        if column_types:
            # Remover created_at se existir no DataFrame
            if 'created_at' in df.columns:
                df = df.drop('created_at', axis=1)
            
            # Filtrar apenas colunas que existem no schema
            valid_columns = [col for col in df.columns if col in column_types or col == 'id']
            if valid_columns:
                df = df[valid_columns]
        
        if df.empty:
            print(f"[AVISO] DataFrame vazio após filtragem")
            return None, None, None, 0
        
        # Gerar conteúdo INSERT
        insert_lines = []
        insert_lines.append(f"-- SQL gerado automaticamente a partir de {os.path.basename(csv_path)}")
        insert_lines.append(f"-- Tabela: {table_name}")
        insert_lines.append(f"-- Registros: {len(df)}")
        insert_lines.append("--")
        insert_lines.append("")
        
        # Gerar INSERT statements em batches
        total_batches = (len(df) + batch_size - 1) // batch_size
        
        for batch_idx in range(total_batches):
            start_idx = batch_idx * batch_size
            end_idx = min(start_idx + batch_size, len(df))
            batch_df = df.iloc[start_idx:end_idx]
            
            # Gerar INSERT statement
            columns_str = ", ".join([f'"{col}"' for col in batch_df.columns])
            
            # Gerar valores para cada linha
            values_lines = []
            for _, row in batch_df.iterrows():
                values = []
                for col in batch_df.columns:
                    value = row[col]
                    col_type = column_types.get(col, None)
                    values.append(escape_sql_value(value, col_type, col))
                
                values_str = ", ".join(values)
                values_lines.append(f"    ({values_str})")
            
            # Adicionar INSERT statement
            if values_lines:
                insert_lines.append(f"INSERT INTO {table_name} ({columns_str}) VALUES")
                insert_lines.append(",\n".join(values_lines))
                insert_lines.append(";")
                insert_lines.append("")
            
            if batch_idx % 10 == 0:
                print(f"  [PROGRESSO] Batch {batch_idx + 1}/{total_batches}")
        
        insert_content = "\n".join(insert_lines)
        print(f"[OK] Conteúdo INSERT gerado: {len(df)} registros")
        return table_name, insert_content, schema_content, len(df)
        
    except Exception as e:
        print(f"[ERRO] Erro ao gerar SQL para {csv_path}: {e}")
        import traceback
        traceback.print_exc()
        return None, None, None, 0


def main():
    """Função principal"""
    print("=== GERADOR DE ARQUIVOS SQL COMPLETOS PARA POPULAÇÃO DO BANCO ===\n")
    
    # Detectar diretórios
    project_root = detect_project_root()
    processed_dir = os.path.join(project_root, "data", "processed")
    schemas_dir = os.path.join(project_root, "database", "schemas")
    complete_dir = os.path.join(project_root, "database", "sql_complete")
    
    # Criar diretório de saída se não existir
    os.makedirs(complete_dir, exist_ok=True)
    
    print(f"[INFO] Diretório do projeto: {project_root}")
    print(f"[INFO] Diretório de dados processados: {processed_dir}")
    print(f"[INFO] Diretório de schemas: {schemas_dir}")
    print(f"[INFO] Diretório de saída SQL: {complete_dir}\n")
    
    # Verificar se os diretórios existem
    if not os.path.exists(processed_dir):
        print(f"[ERRO] Diretório de dados processados não encontrado: {processed_dir}")
        return
    
    # Encontrar todos os CSVs processados
    csv_files = [f for f in os.listdir(processed_dir) if f.endswith('.csv') and 'clean' in f]
    
    csv_success = 0
    csv_errors = 0
    
    if not csv_files:
        print(f"[AVISO] Nenhum CSV processado encontrado em {processed_dir}")
    else:
        print(f"[INFO] Encontrados {len(csv_files)} arquivos CSV processados\n")
        
        # Processar cada CSV e gerar arquivo completo
        for csv_file in sorted(csv_files):
            csv_path = os.path.join(processed_dir, csv_file)
            
            # Encontrar schema correspondente
            schema_path = find_matching_schema(csv_file, schemas_dir)
            
            if not schema_path:
                print(f"[AVISO] Schema não encontrado para {csv_file}, pulando...")
                continue
            
            print(f"\n--- Processando: {csv_file} ---")
            
            # Gerar conteúdo INSERT
            table_name, insert_content, auto_schema, num_records = generate_sql_inserts_content(csv_path, schema_path)
            
            if table_name and insert_content:
                # Ler schema do arquivo ou usar o gerado automaticamente
                try:
                    if schema_path:
                        with open(schema_path, 'r', encoding='utf-8') as f:
                            schema_content = f.read()
                    else:
                        schema_content = auto_schema or ""
                    
                    # Gerar nome do arquivo completo
                    complete_filename = f"{table_name}_complete.sql"
                    complete_path = os.path.join(complete_dir, complete_filename)
                    
                    # Combinar em arquivo completo
                    with open(complete_path, 'w', encoding='utf-8') as f:
                        f.write("-- ============================================\n")
                        f.write(f"-- SQL COMPLETO: {table_name}\n")
                        f.write("-- Este arquivo contém CREATE TABLE e INSERT statements\n")
                        f.write("-- ============================================\n\n")
                        
                        f.write("-- SCHEMA (CREATE TABLE)\n")
                        f.write("-- " + "="*50 + "\n")
                        f.write(schema_content)
                        f.write("\n\n")
                        
                        f.write("-- DADOS (INSERT statements)\n")
                        f.write("-- " + "="*50 + "\n")
                        f.write(insert_content)
                    
                    print(f"[SUCESSO] Arquivo completo gerado: {complete_filename} ({num_records} registros)")
                    csv_success += 1
                except Exception as e:
                    print(f"[ERRO] Erro ao gerar arquivo completo: {e}")
                    csv_errors += 1
            else:
                csv_errors += 1
    
    # Verificar se há arquivos GTFS processados
    print("\n=== VERIFICANDO ARQUIVOS GTFS ===\n")
    
    # Verificar múltiplos locais possíveis para GTFS
    gtfs_locations = [
        os.path.join(processed_dir, "gtfs"),
        os.path.join(project_root, "scripts", "database", "processed"),
    ]
    
    gtfs_success = 0
    gtfs_errors = 0
    
    for gtfs_dir in gtfs_locations:
        if os.path.exists(gtfs_dir):
            print(f"[INFO] Diretório GTFS encontrado: {gtfs_dir}")
            gtfs_files = [f for f in os.listdir(gtfs_dir) if f.endswith('.csv') and 'clean' in f]
            
            if gtfs_files:
                print(f"[INFO] Encontrados {len(gtfs_files)} arquivos GTFS processados\n")
                
                for gtfs_file in sorted(gtfs_files):
                    gtfs_path = os.path.join(gtfs_dir, gtfs_file)
                    
                    print(f"\n--- Processando GTFS: {gtfs_file} ---")
                    
                    # Gerar conteúdo INSERT e schema automaticamente para GTFS
                    table_name, insert_content, schema_content, num_records = generate_sql_inserts_content(gtfs_path, None)
                    
                    if table_name and insert_content and schema_content:
                        # Gerar nome do arquivo completo GTFS
                        gtfs_table_name = f"gtfs_{table_name}"
                        complete_filename = f"{gtfs_table_name}_complete.sql"
                        complete_path = os.path.join(complete_dir, complete_filename)
                        
                        # Ajustar o schema para usar o nome da tabela com prefixo gtfs_
                        schema_content_gtfs = schema_content.replace(f"CREATE TABLE IF NOT EXISTS {table_name}", f"CREATE TABLE IF NOT EXISTS {gtfs_table_name}")
                        
                        # Ajustar PRIMARY KEY para tabelas GTFS específicas
                        import re
                        if 'trips' in table_name.lower():
                            # Remover PRIMARY KEY de route_id se existir
                            schema_content_gtfs = re.sub(r'route_id\s+INTEGER\s+PRIMARY\s+KEY,', 'route_id INTEGER,', schema_content_gtfs)
                            # Garantir que trip_id tem PRIMARY KEY
                            if "trip_id" in schema_content_gtfs and "trip_id" not in schema_content_gtfs.split("PRIMARY KEY")[0]:
                                schema_content_gtfs = re.sub(r'trip_id\s+VARCHAR\(255\),', 'trip_id VARCHAR(255) PRIMARY KEY,', schema_content_gtfs)
                        
                        elif 'calendar_dates' in table_name.lower():
                            # Remover PRIMARY KEY simples de service_id
                            schema_content_gtfs = re.sub(r'service_id\s+VARCHAR\(255\)\s+PRIMARY\s+KEY,', 'service_id VARCHAR(255),', schema_content_gtfs)
                            # Adicionar PRIMARY KEY composta se não existir
                            if "PRIMARY KEY (service_id, date)" not in schema_content_gtfs:
                                schema_content_gtfs = schema_content_gtfs.replace(
                                    "    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                                    "    PRIMARY KEY (service_id, date),\n    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
                                )
                        elif 'fare_rules' in table_name.lower():
                            # Remover PRIMARY KEY simples de fare_id
                            schema_content_gtfs = re.sub(r'fare_id\s+VARCHAR\(255\)\s+PRIMARY\s+KEY,', 'fare_id VARCHAR(255),', schema_content_gtfs)
                            # Adicionar PRIMARY KEY composta se não existir
                            if "PRIMARY KEY (fare_id, route_id)" not in schema_content_gtfs:
                                schema_content_gtfs = schema_content_gtfs.replace(
                                    "    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                                    "    PRIMARY KEY (fare_id, route_id),\n    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
                                )
                        elif 'shapes' in table_name.lower():
                            # Remover PRIMARY KEY simples de shape_id
                            schema_content_gtfs = re.sub(r'shape_id\s+VARCHAR\(255\)\s+PRIMARY\s+KEY,', 'shape_id VARCHAR(255),', schema_content_gtfs)
                            # Adicionar PRIMARY KEY composta se não existir
                            if "PRIMARY KEY (shape_id, shape_pt_sequence)" not in schema_content_gtfs:
                                schema_content_gtfs = schema_content_gtfs.replace(
                                    "    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                                    "    PRIMARY KEY (shape_id, shape_pt_sequence),\n    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
                                )
                        elif 'stop_times' in table_name.lower():
                            # Remover PRIMARY KEY simples de trip_id
                            schema_content_gtfs = re.sub(r'trip_id\s+VARCHAR\(255\)\s+PRIMARY\s+KEY,', 'trip_id VARCHAR(255),', schema_content_gtfs)
                            # Adicionar PRIMARY KEY composta se não existir
                            if "PRIMARY KEY (trip_id, stop_sequence)" not in schema_content_gtfs:
                                schema_content_gtfs = schema_content_gtfs.replace(
                                    "    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                                    "    PRIMARY KEY (trip_id, stop_sequence),\n    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
                                )
                        
                        # Ajustar os INSERTs para usar o nome da tabela com prefixo gtfs_
                        insert_content_gtfs = insert_content.replace(f"INSERT INTO {table_name}", f"INSERT INTO {gtfs_table_name}")
                        
                        # Gerar arquivo completo com CREATE TABLE + INSERT
                        with open(complete_path, 'w', encoding='utf-8') as f:
                            f.write("-- ============================================\n")
                            f.write(f"-- SQL COMPLETO: {gtfs_table_name}\n")
                            f.write("-- Este arquivo contém CREATE TABLE e INSERT statements\n")
                            f.write("-- ============================================\n\n")
                            
                            f.write("-- SCHEMA (CREATE TABLE)\n")
                            f.write("-- " + "="*50 + "\n")
                            f.write(schema_content_gtfs)
                            f.write("\n\n")
                            
                            f.write("-- DADOS (INSERT statements)\n")
                            f.write("-- " + "="*50 + "\n")
                            f.write(insert_content_gtfs)
                        
                        print(f"[SUCESSO] Arquivo completo GTFS gerado: {complete_filename} ({num_records} registros)")
                        gtfs_success += 1
                    else:
                        gtfs_errors += 1
            else:
                print(f"[AVISO] Nenhum arquivo GTFS processado encontrado em {gtfs_dir}")
    
    # Resumo final
    print("\n=== RESUMO ===")
    total_success = csv_success + gtfs_success
    total_errors = csv_errors + gtfs_errors
    
    print(f"[SUCESSO] Arquivos SQL completos gerados: {total_success}")
    print(f"  - CSVs normais: {csv_success}")
    print(f"  - GTFS: {gtfs_success}")
    print(f"[ERRO] Erros: {total_errors}")
    print(f"[INFO] Arquivos completos salvos em: {complete_dir}")


if __name__ == "__main__":
    main()

