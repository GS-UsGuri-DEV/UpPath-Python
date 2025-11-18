"""
routes.py

Define todos os endpoints da API REST do UpPath.
"""

import datetime
from typing import Any

from flask import Blueprint, jsonify

from src.services import DAO as db
from src.services import consultas

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')


def _json_serializer(obj: Any) -> str:
    """Serializa objetos datetime para ISO 8601."""
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    return str(obj)


def _error_response(message: str, status_code: int = 400):
    """Retorna resposta de erro padronizada."""
    return jsonify({'error': message, 'success': False}), status_code


def _success_response(data: Any, message: str = None):
    """Retorna resposta de sucesso padronizada."""
    response = {'success': True, 'data': data}
    if message:
        response['message'] = message
    return jsonify(response), 200


# ============================================================================
# ENDPOINTS DE SAÚDE E INFO
# ============================================================================


@api_bp.route('/health', methods=['GET'])
def health_check():
    """Endpoint para verificar se a API está funcionando."""
    return _success_response(
        {'status': 'healthy', 'timestamp': datetime.datetime.now().isoformat()}
    )


@api_bp.route('/info', methods=['GET'])
def api_info():
    """Retorna informações sobre os endpoints disponíveis."""
    endpoints = {
        'health': '/api/v1/health',
        'user_dashboard': {
            'bem_estar': '/api/v1/dashboard/user/<int:id_user>/bem-estar',
            'trilhas': '/api/v1/dashboard/user/<int:id_user>/trilhas',
            'recomendacoes': '/api/v1/dashboard/user/<int:id_user>/recomendacoes',
            'completo': '/api/v1/dashboard/user/<int:id_user>/completo',
        },
        'company_dashboard': {
            'nivel_carreira': '/api/v1/dashboard/company/<int:id_empresa>/nivel-carreira',
            'bem_estar': '/api/v1/dashboard/company/<int:id_empresa>/bem-estar',
            'trilhas': '/api/v1/dashboard/company/<int:id_empresa>/trilhas',
            'baixa_motivacao': '/api/v1/dashboard/company/<int:id_empresa>/baixa-motivacao',
            'completo': '/api/v1/dashboard/company/<int:id_empresa>/completo',
        },
    }
    return _success_response(endpoints, 'API UpPath v1.0')


# ============================================================================
# DASHBOARD INDIVIDUAL (USUÁRIO)
# ============================================================================


@api_bp.route('/dashboard/user/<int:id_user>/bem-estar', methods=['GET'])
def user_bem_estar(id_user: int):
    """Retorna evolução do bem-estar do usuário."""
    try:
        with db.get_cursor() as cursor:
            dados = consultas.consulta_bem_estar_user(cursor, id_user)
            return _success_response(dados)
    except Exception as e:
        return _error_response(f'Erro ao buscar bem-estar: {str(e)}', 500)


@api_bp.route('/dashboard/user/<int:id_user>/trilhas', methods=['GET'])
def user_trilhas(id_user: int):
    """Retorna progresso nas trilhas do usuário."""
    try:
        with db.get_cursor() as cursor:
            dados = consultas.consulta_progresso_trilhas_user(cursor, id_user)
            return _success_response(dados)
    except Exception as e:
        return _error_response(f'Erro ao buscar trilhas: {str(e)}', 500)


@api_bp.route('/dashboard/user/<int:id_user>/recomendacoes', methods=['GET'])
def user_recomendacoes(id_user: int):
    """Retorna recomendações recebidas pelo usuário."""
    try:
        with db.get_cursor() as cursor:
            dados = consultas.consulta_recomendacoes_user(cursor, id_user)
            return _success_response(dados)
    except Exception as e:
        return _error_response(f'Erro ao buscar recomendações: {str(e)}', 500)


@api_bp.route('/dashboard/user/<int:id_user>/completo', methods=['GET'])
def user_dashboard_completo(id_user: int):
    """Retorna dashboard completo do usuário com todas as informações."""
    try:
        with db.get_cursor() as cursor:
            dashboard = {
                'id_usuario': id_user,
                'bem_estar': consultas.consulta_bem_estar_user(cursor, id_user),
                'trilhas': consultas.consulta_progresso_trilhas_user(cursor, id_user),
                'recomendacoes': consultas.consulta_recomendacoes_user(cursor, id_user),
            }
            return _success_response(dashboard)
    except Exception as e:
        return _error_response(f'Erro ao buscar dashboard: {str(e)}', 500)


# ============================================================================
# DASHBOARD CORPORATIVO (EMPRESA)
# ============================================================================


@api_bp.route('/dashboard/company/<int:id_empresa>/nivel-carreira', methods=['GET'])
def company_nivel_carreira(id_empresa: int):
    """Retorna distribuição de níveis de carreira na empresa."""
    try:
        with db.get_cursor() as cursor:
            dados = consultas.consulta_distribuicao_nivel_carreira(cursor, id_empresa)
            return _success_response(dados)
    except Exception as e:
        return _error_response(f'Erro ao buscar níveis de carreira: {str(e)}', 500)


@api_bp.route('/dashboard/company/<int:id_empresa>/bem-estar', methods=['GET'])
def company_bem_estar(id_empresa: int):
    """Retorna média de bem-estar da empresa."""
    try:
        with db.get_cursor() as cursor:
            dados = consultas.consulta_media_bem_estar_empresa(cursor, id_empresa)
            return _success_response(dados)
    except Exception as e:
        return _error_response(f'Erro ao buscar bem-estar da empresa: {str(e)}', 500)


@api_bp.route('/dashboard/company/<int:id_empresa>/trilhas', methods=['GET'])
def company_trilhas(id_empresa: int):
    """Retorna trilhas mais utilizadas na empresa."""
    try:
        with db.get_cursor() as cursor:
            dados = consultas.consulta_trilhas_mais_utilizadas_empresa(
                cursor, id_empresa
            )
            return _success_response(dados)
    except Exception as e:
        return _error_response(f'Erro ao buscar trilhas da empresa: {str(e)}', 500)


@api_bp.route('/dashboard/company/<int:id_empresa>/baixa-motivacao', methods=['GET'])
def company_baixa_motivacao(id_empresa: int):
    """Retorna funcionários com baixa motivação (<5)."""
    try:
        with db.get_cursor() as cursor:
            dados = consultas.consulta_funcionarios_baixa_motivacao(cursor, id_empresa)
            return _success_response(dados)
    except Exception as e:
        return _error_response(
            f'Erro ao buscar funcionários com baixa motivação: {str(e)}', 500
        )


@api_bp.route('/dashboard/company/<int:id_empresa>/completo', methods=['GET'])
def company_dashboard_completo(id_empresa: int):
    """Retorna dashboard completo da empresa com todas as informações."""
    try:
        with db.get_cursor() as cursor:
            dashboard = {
                'id_empresa': id_empresa,
                'nivel_carreira': consultas.consulta_distribuicao_nivel_carreira(
                    cursor, id_empresa
                ),
                'bem_estar': consultas.consulta_media_bem_estar_empresa(
                    cursor, id_empresa
                ),
                'trilhas': consultas.consulta_trilhas_mais_utilizadas_empresa(
                    cursor, id_empresa
                ),
                'baixa_motivacao': consultas.consulta_funcionarios_baixa_motivacao(
                    cursor, id_empresa
                ),
            }
            return _success_response(dashboard)
    except Exception as e:
        return _error_response(f'Erro ao buscar dashboard da empresa: {str(e)}', 500)


# ============================================================================
# TRATAMENTO DE ERROS
# ============================================================================


@api_bp.errorhandler(404)
def not_found(error):
    """Tratamento para rotas não encontradas."""
    return _error_response('Endpoint não encontrado', 404)


@api_bp.errorhandler(500)
def internal_error(error):
    """Tratamento para erros internos do servidor."""
    return _error_response('Erro interno do servidor', 500)
