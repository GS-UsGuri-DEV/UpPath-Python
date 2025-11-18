# API UpPath - Documentação

API REST para exposição de dados e dashboards do sistema UpPath.

## Instalação

```bash
pip install -r requirements.txt
```

## Configuração

Certifique-se de ter o arquivo `.env` configurado com as credenciais do Oracle:

```
ORACLE_USER=seu_usuario
ORACLE_PASSWORD=sua_senha
ORACLE_DSN=seu_dsn
```

## Executar a API

```bash
python src/api/app.py
```

A API estará disponível em: `http://localhost:5000`

## Endpoints Disponíveis

### Informações e Saúde

- **GET** `/` - Informações básicas da API
- **GET** `/api/v1/info` - Lista completa de endpoints
- **GET** `/api/v1/health` - Verificação de saúde da API

### Dashboard Individual (Usuário)

- **GET** `/api/v1/dashboard/user/<id_user>/bem-estar` - Evolução do bem-estar
- **GET** `/api/v1/dashboard/user/<id_user>/trilhas` - Progresso nas trilhas
- **GET** `/api/v1/dashboard/user/<id_user>/recomendacoes` - Recomendações recebidas
- **GET** `/api/v1/dashboard/user/<id_user>/completo` - Dashboard completo do usuário

### Dashboard Corporativo (Empresa)

- **GET** `/api/v1/dashboard/company/<id_empresa>/nivel-carreira` - Distribuição de níveis de carreira
- **GET** `/api/v1/dashboard/company/<id_empresa>/bem-estar` - Média de bem-estar da empresa
- **GET** `/api/v1/dashboard/company/<id_empresa>/trilhas` - Trilhas mais utilizadas
- **GET** `/api/v1/dashboard/company/<id_empresa>/baixa-motivacao` - Funcionários com baixa motivação
- **GET** `/api/v1/dashboard/company/<id_empresa>/completo` - Dashboard completo da empresa

## Exemplos de Uso

### Usando curl

```bash
# Health check
curl http://localhost:5000/api/v1/health

# Dashboard completo do usuário ID 1
curl http://localhost:5000/api/v1/dashboard/user/1/completo

# Dashboard completo da empresa ID 1
curl http://localhost:5000/api/v1/dashboard/company/1/completo

# Lista de empresas
curl http://localhost:5000/api/v1/empresas/contagem
```

### Usando JavaScript (Fetch API)

```javascript
// Dashboard do usuário
fetch("http://localhost:5000/api/v1/dashboard/user/1/completo")
  .then((response) => response.json())
  .then((data) => {
    console.log("Dashboard do usuário:", data);
    // Atualizar gráficos aqui
  })
  .catch((error) => console.error("Erro:", error));

// Dashboard da empresa
fetch("http://localhost:5000/api/v1/dashboard/company/1/completo")
  .then((response) => response.json())
  .then((data) => {
    console.log("Dashboard da empresa:", data);
    // Atualizar gráficos aqui
  })
  .catch((error) => console.error("Erro:", error));
```

### Usando Python (requests)

```python
import requests

# Dashboard do usuário
response = requests.get('http://localhost:5000/api/v1/dashboard/user/1/completo')
dashboard = response.json()
print(dashboard['data'])

# Dashboard da empresa
response = requests.get('http://localhost:5000/api/v1/dashboard/company/1/completo')
dashboard = response.json()
print(dashboard['data'])
```

## Formato de Resposta

### Sucesso

```json
{
  "success": true,
  "data": {
    // dados da consulta
  },
  "message": "Mensagem opcional"
}
```

### Erro

```json
{
  "success": false,
  "error": "Mensagem de erro"
}
```

## Estrutura dos Dados

### Dashboard do Usuário

```json
{
  "success": true,
  "data": {
    "id_usuario": 1,
    "bem_estar": [
      {
        "data_registro": "2025-11-01T10:00:00",
        "nivel_estresse": 7,
        "nivel_motivacao": 8,
        "qualidade_sono": 6
      }
    ],
    "trilhas": [
      {
        "nome_trilha": "Python Avançado",
        "progresso_percentual": 75,
        "status": "Em andamento"
      }
    ],
    "recomendacoes": [
      {
        "tipo": "Curso",
        "id_referencia": 123,
        "motivo": "Baseado no seu perfil",
        "data_recomendacao": "2025-11-15T14:30:00"
      }
    ]
  }
}
```

### Dashboard da Empresa

```json
{
  "success": true,
  "data": {
    "id_empresa": 1,
    "nivel_carreira": [
      {
        "nivel_carreira": "Sênior",
        "total": 15
      },
      {
        "nivel_carreira": "Pleno",
        "total": 25
      }
    ],
    "bem_estar": {
      "media_estresse": 5.5,
      "media_motivacao": 7.2,
      "media_sono": 6.8
    },
    "trilhas": [
      {
        "nome_trilha": "Liderança",
        "total_usuarios": 30
      }
    ],
    "baixa_motivacao": [
      {
        "nome_completo": "João Silva",
        "nivel_motivacao": 3,
        "data_registro": "2025-11-17T09:00:00"
      }
    ]
  }
}
```

## CORS

A API está configurada para aceitar requisições de qualquer origem durante o desenvolvimento.
Em produção, configure o CORS para aceitar apenas domínios específicos editando `src/api/app.py`:

```python
CORS(app, resources={
    r'/api/*': {
        'origins': ['https://seu-dominio.com'],
        # ...
    }
})
```

## Troubleshooting

### Erro de conexão com o banco

Verifique se:

- As variáveis de ambiente estão configuradas corretamente
- O banco Oracle está acessível
- As credenciais estão corretas

### Erro de CORS

Se estiver recebendo erros de CORS no navegador:

- Verifique se a API está rodando
- Confirme que o CORS está habilitado no `app.py`
- Em desenvolvimento, use um proxy ou configure o CORS para aceitar todas as origens

### Porta já em uso

Se a porta 5000 já estiver em uso, altere em `app.py`:

```python
app.run(debug=True, host='0.0.0.0', port=5001)  # ou outra porta
```
