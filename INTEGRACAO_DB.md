# Guia de Integração com PostgreSQL (Cloud)

Este guia explica como integrar os dados do projeto no banco PostgreSQL na cloud.

## 📋 Pré-requisitos

1. ✅ Banco PostgreSQL configurado na cloud (Neon ou outro)
2. ✅ Credenciais de acesso ao banco
3. ✅ Python 3.8+ instalado
4. ✅ Dependências instaladas: `pip install -r requirements.txt`

## 🔧 Passo 1: Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto com as credenciais do banco:

```bash
# Opção 1: Usar DATABASE_URL (formato completo)
DATABASE_URL=postgresql://usuario:senha@host:porta/database


**⚠️ IMPORTANTE:** 
- O arquivo `.env` não deve ser commitado no Git (já deve estar no `.gitignore`)
- Use as credenciais fornecidas pelo seu provedor de cloud (Neon, AWS RDS, etc.)

## 🧪 Passo 2: Testar Conexão

Antes de carregar os dados, teste se a conexão está funcionando:

```bash
python scripts/utils/teste_conexao.py
```

Se tudo estiver correto, você verá:
```
✅ Conexão estabelecida com sucesso!
   📊 Banco: seu-banco
   👤 Usuário: seu-usuario
   🔧 PostgreSQL: PostgreSQL 15.x
```

## 🗄️ Passo 3: Criar Tabelas no Banco

Execute o script para criar todas as tabelas definidas nos schemas:

```bash
python scripts/database/setup_database.py
```

Este script irá:
- ✅ Conectar ao banco
- ✅ Criar/verificar todas as tabelas:
  - `equipamentos_medicao_velocidade`
  - `semaforos`
  - `monitoramento_cttu`
  - `fluxo_veiculos_hora`
  - `fluxo_velocidade_15min`
  - `relatorio_fluxo_agosto`
  - `relatorio_fluxo_fevereiro`

## 📊 Passo 4: Carregar Dados

Após criar as tabelas, carregue os dados dos CSVs processados:

```bash
python scripts/database/load_data.py
```

Este script irá:
- ✅ Ler os CSVs da pasta `data/processed/`
- ✅ Validar e limpar os dados
- ✅ Carregar no banco (usa TRUNCATE antes de inserir - limpa dados existentes)

**Arquivos carregados:**
- `equipamentos_medicao_velocidade_clean.csv` → `equipamentos_medicao_velocidade`
- `semaforos_clean.csv` → `semaforos`
- `monitoramento_cttu_clean.csv` → `monitoramento_cttu`
- `fluxo_veiculos_hora_clean.csv` → `fluxo_veiculos_hora`
- `fluxo_velocidade_15min_clean.csv` → `fluxo_velocidade_15min`
- `relatorio_fluxo_agosto_2025_clean.csv` → `relatorio_fluxo_agosto`
- `relatorio_fluxo_fevereiro_2025_clean.csv` → `relatorio_fluxo_fevereiro`

 
## ⚠️ Observações Importantes

1. **TRUNCATE**: O script `load_data.py` limpa a tabela antes de inserir (usa `TRUNCATE TABLE`). Se quiser manter dados existentes, comente a linha 113 do script.

2. **Colunas Duplicadas**: O script trata automaticamente colunas duplicadas nos CSVs (mantém apenas a primeira ocorrência).

3. **Validação**: O script valida que as colunas do CSV correspondem às colunas da tabela antes de inserir.



### Erro de conexão
- Verifique se as credenciais no `.env` estão corretas
- Teste a conexão com: `python scripts/utils/teste_conexao.py`

### Erro ao criar tabelas
- Verifique se as tabelas já existem (o script usa `CREATE TABLE IF NOT EXISTS`)

 



 

