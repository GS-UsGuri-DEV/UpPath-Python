# UpPath - Sistema de Gestão de Usuários

Sistema Python CRUD completo para gerenciamento de usuários com Oracle Database, desenvolvido para a disciplina Computational Thinking Using Python.

## 🎯 Características

- ✅ **CRUD Completo**: Create, Read, Update, Delete de usuários
- ✅ **Menu Interativo**: Interface terminal amigável
- ✅ **Validações**: Entrada de dados validada (email, datas, tamanhos)
- ✅ **Tratamento de Exceções**: Erros tratados com mensagens claras
- ✅ **Modularização**: Código organizado em funções reutilizáveis
- ✅ **Logging**: Auditoria de operações
- ✅ **Connection Pooling**: Performance otimizada para produção
- ✅ **Segurança**: Senhas armazenadas com hash SHA-256
- ✅ **Geração de IDs**: Sequence Oracle com fallback seguro

## 📋 Pré-requisitos

- Python 3.8+
- Oracle Database (11g ou superior)
- Driver Oracle: `oracledb`

## 🔧 Instalação

### 1. Clone o repositório

```bash
git clone <seu-repositorio>
cd UpPath-Python
```

### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

### 3. Configure as variáveis de ambiente

Crie um arquivo `.env` ou configure as variáveis no sistema:

```bash
# Windows (cmd)
set ORACLE_USER=seu_usuario
set ORACLE_PASSWORD=sua_senha
set ORACLE_DSN=localhost:1521/XEPDB1

# Windows (PowerShell)
$env:ORACLE_USER="seu_usuario"
$env:ORACLE_PASSWORD="sua_senha"
$env:ORACLE_DSN="localhost:1521/XEPDB1"

# Linux/Mac
export ORACLE_USER=seu_usuario
export ORACLE_PASSWORD=sua_senha
export ORACLE_DSN=localhost:1521/XEPDB1
```

## 🚀 Como Usar

### Execução via main.py (Recomendado)

```bash
python main.py
```

O sistema irá:

1. Inicializar o banco de dados (criar tabelas e sequences)
2. Configurar pool de conexões
3. Exibir o menu interativo

### Menu Principal

```
1 - Criar usuário
2 - Listar usuários
3 - Buscar usuário por ID
4 - Atualizar usuário
5 - Deletar usuário
0 - Sair
```

## 📁 Estrutura do Projeto

```
UpPath-Python/
├── main.py                 # Ponto de entrada principal
├── storage_oracle.py       # Camada de acesso ao banco Oracle
├── crud_usuarios.py        # Funções CRUD e UI
├── requirements.txt        # Dependências Python
├── README.md              # Esta documentação
└── .github/
    └── instructions/
        └── regras.instructions.md
```

## 🗄️ Modelo de Dados

### Tabela: EMPRESAS

| Coluna        | Tipo                | Descrição           |
| ------------- | ------------------- | ------------------- |
| id_empresa    | NUMBER(6) PK        | ID único da empresa |
| nome_empresa  | VARCHAR2(60)        | Nome da empresa     |
| cnpj          | VARCHAR2(18) UNIQUE | CNPJ                |
| email_contato | VARCHAR2(60) UNIQUE | Email de contato    |
| data_cadastro | TIMESTAMP           | Data de cadastro    |

### Tabela: USUARIOS

| Coluna          | Tipo                | Descrição                       |
| --------------- | ------------------- | ------------------------------- |
| id_usuario      | NUMBER(6) PK        | ID único do usuário             |
| id_empresa      | NUMBER(6) FK        | Referência à empresa (opcional) |
| nome_completo   | VARCHAR2(60)        | Nome completo                   |
| email           | VARCHAR2(60) UNIQUE | Email                           |
| senha_hash      | VARCHAR2(80)        | Hash SHA-256 da senha           |
| nivel_carreira  | VARCHAR2(30)        | Júnior/Pleno/Sênior             |
| ocupacao        | VARCHAR2(30)        | Cargo/função                    |
| genero          | VARCHAR2(15)        | Gênero                          |
| data_nascimento | DATE                | Data de nascimento              |
| data_cadastro   | TIMESTAMP           | Data de registro                |
| is_admin        | NUMBER(1)           | Flag administrador (0/1)        |

## 🔐 Segurança

- **Senhas**: Armazenadas com hash SHA-256
- **SQL Injection**: Proteção via bind parameters
- **Validações**: Email, tamanhos de campos, tipos de dados

## ⚙️ Configurações Avançadas

### Pool de Conexões

Edite em `main.py`:

```python
db.init_pool(min_connections=2, max_connections=10)
```

### Logging

Configure o nível de log em `storage_oracle.py`:

```python
logging.basicConfig(level=logging.DEBUG)  # DEBUG, INFO, WARNING, ERROR
```

## 🐛 Troubleshooting

### Erro: "oracledb não encontrado"

```bash
pip install oracledb
```

### Erro: "Informação de conexão Oracle incompleta"

Verifique se as variáveis de ambiente estão configuradas:

```bash
echo %ORACLE_USER%       # Windows cmd
echo $env:ORACLE_USER    # PowerShell
echo $ORACLE_USER        # Linux/Mac
```

### Erro ao criar tabelas

- Verifique permissões do usuário Oracle
- Confirme que o DSN está correto
- Teste a conexão manualmente

## 📚 Referências

- [Oracle Database Documentation](https://docs.oracle.com/en/database/)
- [python-oracledb](https://python-oracledb.readthedocs.io/)
- [PEP 249 – Python Database API](https://www.python.org/dev/peps/pep-0249/)

## 👥 Autores

Desenvolvido para a disciplina **Computational Thinking Using Python** - FIAP

## 📄 Licença

Este projeto está sob a licença especificada no arquivo LICENSE.
