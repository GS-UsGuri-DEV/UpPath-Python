"""
app.py

Aplicação Flask principal da API UpPath.
"""

import sys
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

# Adicionar raiz do projeto ao path
project_root = Path(__file__).parent.parent.parent.resolve()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.api.routes import api_bp  # noqa: E402

# Carregar variáveis de ambiente
env_path = project_root / '.env'
load_dotenv(dotenv_path=env_path)


def create_app():
    """Factory function para criar a aplicação Flask."""
    app = Flask(__name__)

    # Configurações
    app.config['JSON_SORT_KEYS'] = False
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

    # Habilitar CORS para permitir requisições do frontend
    CORS(
        app,
        resources={
            r'/api/*': {
                'origins': '*',  # Em produção, especifique os domínios permitidos
                'methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
                'allow_headers': ['Content-Type', 'Authorization'],
            }
        },
    )

    # Registrar blueprints
    app.register_blueprint(api_bp)

    @app.route('/')
    def index():
        """Rota raiz com informações básicas."""
        return {
            'name': 'UpPath API',
            'version': '1.0.0',
            'description': 'API REST para gestão de usuários e dashboards do UpPath',
            'endpoints': {
                'info': '/api/v1/info',
                'health': '/api/v1/health',
                'docs': '/api/v1/info',
            },
        }

    return app


if __name__ == '__main__':
    app = create_app()
    print('=' * 60)
    print('UpPath API - Servidor iniciado')
    print('=' * 60)
    print('Documentação: http://localhost:5000/api/v1/info')
    print('Health check: http://localhost:5000/api/v1/health')
    print('=' * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)
