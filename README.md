# UpPath - Sistema de Gestão de Usuários

Sistema Python CRUD completo para gerenciamento de usuários e empresas com Oracle Database, desenvolvido para a disciplina Computational Thinking Using Python.

## 🌐 API em Produção

**A API REST está disponível em:** `https://uppath-python.onrender.com`

- 🚀 **Dashboard do Usuário:** `/api/v1/dashboard/user/{id}/completo`
- 🏢 **Dashboard da Empresa:** `/api/v1/dashboard/company/{id}/completo`
- 💚 **Health Check:** `/api/v1/health`

📖 **Documentação completa:** [API Docs](src/api/docs/API_DOCUMENTATION.md)

---

## 🎯 Características

- ✅ **CRUD Completo**: Create, Read, Update, Delete de usuários
- ✅ **Menu Interativo**: Interface terminal amigável para todas as operações
- ✅ **API REST**: Endpoints JSON para integração com frontend (Flask)
- ✅ **Validações**: Entrada de dados validada (email, datas, tamanhos, CNPJ, etc)
- ✅ **Tratamento de Exceções**: Erros tratados com mensagens claras e robustez
- ✅ **Modularização**: Código organizado em funções reutilizáveis
- ✅ **Exportação de Consultas**: Resultados de consultas podem ser exportados para arquivos JSON
- ✅ **Dashboards**: Painéis individuais (usuário) e corporativos (empresa)
- ✅ **CORS Habilitado**: API configurada para acesso cross-origin
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

### Modo 1: Sistema CRUD via Terminal (Recomendado para CLI)

```bash
python src/main.py
```

O sistema irá:

1. Inicializar o banco de dados (criar tabelas e sequences)
2. Configurar pool de conexões
3. Exibir o menu interativo

### Modo 2: API REST para Frontend

**Produção (Render):**

A API está disponível em: `https://uppath-python.onrender.com`

**Desenvolvimento Local:**

```bash
python src/api/app.py
```

A API local estará em: `http://localhost:5000`

**Documentação Completa:** [API Documentation](src/api/docs/API_DOCUMENTATION.md)

**Endpoints Principais:**
- `GET /api/v1/health` - Verificação de saúde
- `GET /api/v1/dashboard/user/{id}/completo` - Dashboard do usuário
- `GET /api/v1/dashboard/company/{id}/completo` - Dashboard da empresa

### Modo 3: Demo Dashboard HTML

Abra o arquivo `dashboard_demo.html` no navegador para testar a integração com a API em tempo real.

### Menus Interativos

**Menu Principal:**

```
1 - Criar usuário
2 - Listar usuários
3 - Buscar usuário por ID
4 - Atualizar usuário
5 - Deletar usuário
6 - Querries
0 - Sair
```

**Menu Querries:**

```
1 - Painel individual (usuário)
2 - Painel corporativo (empresa)
3 - Empresas (contagem de funcionários)
0 - Voltar ao menu principal
```

**Consultas e Exportação:**
O sistema oferece pelo menos 3 consultas relevantes ao banco Oracle, com opção de exportar o resultado para JSON:

- Distribuição de níveis de carreira por empresa
- Média de bem-estar da empresa
- Evolução do bem-estar do usuário

## 📁 Estrutura do Projeto

```
UpPath-Python/
├── src/
│   ├── main.py                # Ponto de entrada principal (CLI)
│   ├── config.py              # Configurações globais
│   ├── api/                   # API REST
│   │   ├── __init__.py
│   │   ├── app.py            # Aplicação Flask
│   │   └── routes.py         # Endpoints da API
│   ├── data/                  # Pasta para arquivos exportados e dados
│   ├── models/                # Modelos de dados
│   ├── services/              # DAO, storage, consultas, exceções
│   │   ├── DAO.py
│   │   ├── empresa_dao.py
│   │   ├── usuario_dao.py
│   │   ├── storage.py
│   │   ├── consultas.py
│   │   └── exceptions.py
│   ├── ui/                    # Interface de usuário (menus e CRUD)
│   │   ├── crud_usuarios.py
│   │   └── painel_queries.py
│   └── utils/                 # Utilitários (validações, mensagens, helpers)
│       ├── color_msg.py
│       ├── db_utils.py
│       ├── validators.py
│       └── __init__.py
├── test_api.py                # Script de teste da API
├── dashboard_demo.html        # Demo de dashboard em HTML/JS
├── API_DOCUMENTATION.md       # Documentação completa da API
├── requirements.txt           # Dependências Python
└── README.md                  # Esta documentação
```

## 🗄️ Modelo de Dados

```sql
CREATE TABLE empresas (
	id_empresa NUMBER(6) NOT NULL,
	nome_empresa VARCHAR2(60) NOT NULL,
	cnpj VARCHAR2(18) NOT NULL,
	email_contato VARCHAR2(60) NOT NULL,
	data_cadastro TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL,
	CONSTRAINT empresas_PK PRIMARY KEY (id_empresa),
	CONSTRAINT empresas_cnpj_uk UNIQUE (cnpj),
	CONSTRAINT empresas_email_uk UNIQUE (email_contato)
);

CREATE TABLE usuarios (
	id_usuario NUMBER(6) NOT NULL,
	id_empresa NUMBER(6),
	nome_completo VARCHAR2(60) NOT NULL,
	email VARCHAR2(60) NOT NULL,
	senha_hash VARCHAR2(80) NOT NULL,
	nivel_carreira VARCHAR2(30) NOT NULL,
	ocupacao VARCHAR2(30) NOT NULL,
	genero VARCHAR2(15) NOT NULL,
	data_nascimento DATE NOT NULL,
	data_cadastro TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL,
	is_admin NUMBER(1) DEFAULT 0 NOT NULL,
	CONSTRAINT usuarios_PK PRIMARY KEY (id_usuario),
	CONSTRAINT usuarios_email_uk UNIQUE (email),
	CONSTRAINT usuarios_empresas_FK FOREIGN KEY (id_empresa) REFERENCES empresas(id_empresa)
);

-- Tabela TRILHAS
CREATE TABLE trilhas (
	id_trilha NUMBER(6) NOT NULL,
	nome_trilha VARCHAR2(40) NOT NULL,
	descricao_trilha VARCHAR2(400) NOT NULL,
	imagem_trilha BLOB,
	imagem_trilha_nome VARCHAR2(255),
	imagem_trilha_mime VARCHAR2(100),
	imagem_trilha_tamanho NUMBER(10),
	imagem_trilha_alt VARCHAR2(200),
	imagem_trilha_thumb BLOB,
	categoria VARCHAR2(30) NOT NULL,
	nivel_dificuldade VARCHAR2(15) NOT NULL,
	data_criacao TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL,
	CONSTRAINT trilhas_PK PRIMARY KEY (id_trilha),
	CONSTRAINT ck_nivel_dificuldade CHECK (nivel_dificuldade IN ('Iniciante', 'Intermediário', 'Avançado'))
);

-- Tabela CURSOS
CREATE TABLE cursos (
	id_curso NUMBER(6) NOT NULL,
	id_trilha NUMBER(6) NOT NULL,
	titulo VARCHAR2(80) NOT NULL,
	descricao_curso VARCHAR2(400) NOT NULL,
	imagem_curso BLOB,
	imagem_curso_nome VARCHAR2(255),
	imagem_curso_mime VARCHAR2(100),
	imagem_curso_tamanho NUMBER(10),
	imagem_curso_alt VARCHAR2(200),
	imagem_curso_thumb BLOB,
	plataforma VARCHAR2(30) NOT NULL,
	link_curso VARCHAR2(500) NOT NULL,
	duracao_horas NUMBER(3) NOT NULL,
	CONSTRAINT cursos_PK PRIMARY KEY (id_curso),
	CONSTRAINT cursos_link_curso_uk UNIQUE (link_curso),
	CONSTRAINT cursos_trilhas_FK FOREIGN KEY (id_trilha) REFERENCES trilhas(id_trilha),
	CONSTRAINT ck_duracao_horas CHECK (duracao_horas > 0)
);

-- Tabela USUARIO_TRILHA
CREATE TABLE usuario_trilha (
	id_usuario NUMBER(6) NOT NULL,
	id_trilha NUMBER(6) NOT NULL,
	data_inicio TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL,
	progresso_percentual NUMBER(3) NOT NULL,
	status VARCHAR2(15) NOT NULL,
	CONSTRAINT usuario_trilha_PK PRIMARY KEY (id_usuario, id_trilha),
	CONSTRAINT usuario_trilha_usuarios_FK FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
	CONSTRAINT usuario_trilha_trilhas_FK FOREIGN KEY (id_trilha) REFERENCES trilhas(id_trilha),
	CONSTRAINT ck_progresso_percentual CHECK (progresso_percentual BETWEEN 0 AND 100)
);

-- Tabela BEM_ESTAR
CREATE TABLE bem_estar (
	id_registro NUMBER(8) NOT NULL,
	id_usuario NUMBER(6) NOT NULL,
	data_registro TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL,
	nivel_estresse NUMBER(2) NOT NULL,
	nivel_motivacao NUMBER(2) NOT NULL,
	qualidade_sono NUMBER(2) NOT NULL,
	observacao VARCHAR2(200),
	CONSTRAINT bem_estar_PK PRIMARY KEY (id_registro),
	CONSTRAINT bem_estar_usuarios_FK FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
	CONSTRAINT ck_nivel_estresse CHECK (nivel_estresse BETWEEN 0 AND 10),
	CONSTRAINT ck_nivel_motivacao CHECK (nivel_motivacao BETWEEN 0 AND 10),
	CONSTRAINT ck_qualidade_sono CHECK (qualidade_sono BETWEEN 0 AND 10)
);
-- Tabela RECOMENDACOES
CREATE TABLE recomendacoes (
	id_recomendacao NUMBER(8) NOT NULL,
	id_usuario NUMBER(6) NOT NULL,
	tipo VARCHAR2(7) NOT NULL,
	id_referencia NUMBER(6) NOT NULL,
	motivo VARCHAR2(120) NOT NULL,
	data_recomendacao TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL,
	CONSTRAINT recomendacoes_PK PRIMARY KEY (id_recomendacao),
	CONSTRAINT recomendacoes_usuarios_FK FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
	CONSTRAINT ck_tipo_recomendacao CHECK (tipo IN ('Curso', 'Trilha'))
);
```

## 🔐 Segurança

- **Senhas**: Armazenadas com hash SHA-256
- **Validações**: Email, tamanhos de campos, tipos de dados, CNPJ
- **Tratamento de Exceções**: Todas as operações possuem try-except para robustez

## ⚙️ Configurações Avançadas

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
