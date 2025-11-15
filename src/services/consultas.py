"""
consultas.py

Funções para consultas personalizadas (dashboard individual e corporativo).
Retornam listas de dicionários prontos para exportação em JSON.
"""

from typing import Any, Dict, List

from utils.validators import ValidationError

# Todas as funções recebem um cursor Oracle e parâmetros validados


def consulta_bem_estar_user(cursor, id_user: int) -> List[Dict[str, Any]]:
    """
    Consulta evolução do bem-estar do usuário.
    Retorna lista de dicts: [{data, estresse, motivacao, sono}, ...]
    """
    try:
        if not isinstance(id_user, int):
            raise ValidationError('ID do usuário inválido')
        cursor.execute(
            """
            SELECT 
                data_registro,
                nivel_estresse,
                nivel_motivacao,
                qualidade_sono
            FROM bem_estar
            WHERE id_usuario = :id_user
            ORDER BY data_registro
            """,
            {'id_user': id_user},
        )
        colunas = [col[0].lower() for col in cursor.description]
        return [dict(zip(colunas, linha)) for linha in cursor.fetchall()]
    except Exception as e:
        return [{'error': str(e)}]


def consulta_progresso_trilhas_user(cursor, id_user: int) -> List[Dict[str, Any]]:
    """
    Consulta progresso nas trilhas do usuário.
    Retorna lista de dicts: [{nome_trilha, progresso_percentual, status}, ...]
    """
    try:
        if not isinstance(id_user, int):
            raise ValidationError('ID do usuário inválido')
        cursor.execute(
            """
            SELECT 
                t.nome_trilha,
                ut.progresso_percentual,
                ut.status
            FROM usuario_trilha ut
            JOIN trilhas t ON ut.id_trilha = t.id_trilha
            WHERE ut.id_usuario = :id_user
            """,
            {'id_user': id_user},
        )
        colunas = [col[0].lower() for col in cursor.description]
        return [dict(zip(colunas, linha)) for linha in cursor.fetchall()]
    except Exception as e:
        return [{'error': str(e)}]


def consulta_recomendacoes_user(cursor, id_user: int) -> List[Dict[str, Any]]:
    """
    Consulta recomendações recebidas pelo usuário.
    Retorna lista de dicts: [{tipo, id_referencia, motivo, data_recomendacao}, ...]
    """
    try:
        if not isinstance(id_user, int):
            raise ValidationError('ID do usuário inválido')
        cursor.execute(
            """
            SELECT 
                tipo,
                id_referencia,
                motivo,
                data_recomendacao
            FROM recomendacoes
            WHERE id_usuario = :id_user
            ORDER BY data_recomendacao DESC
            """,
            {'id_user': id_user},
        )
        colunas = [col[0].lower() for col in cursor.description]
        return [dict(zip(colunas, linha)) for linha in cursor.fetchall()]
    except Exception as e:
        return [{'error': str(e)}]


def consulta_distribuicao_nivel_carreira(
    cursor, id_empresa: int
) -> List[Dict[str, Any]]:
    """
    Consulta distribuição de níveis de carreira na empresa.
    Retorna lista de dicts: [{nivel_carreira, total}, ...]
    """
    try:
        if not isinstance(id_empresa, int):
            raise ValidationError('ID da empresa inválido')
        cursor.execute(
            """
            SELECT nivel_carreira, COUNT(*) AS total
            FROM usuarios
            WHERE id_empresa = :id_empresa
            GROUP BY nivel_carreira
            ORDER BY total DESC
            """,
            {'id_empresa': id_empresa},
        )
        colunas = [col[0].lower() for col in cursor.description]
        return [dict(zip(colunas, linha)) for linha in cursor.fetchall()]
    except Exception as e:
        return [{'error': str(e)}]


def consulta_media_bem_estar_empresa(cursor, id_empresa: int) -> Dict[str, Any]:
    """
    Consulta média de bem-estar da empresa.
    Retorna dict: {media_estresse, media_motivacao, media_sono}
    """
    try:
        if not isinstance(id_empresa, int):
            raise ValidationError('ID da empresa inválido')
        cursor.execute(
            """
            SELECT 
                ROUND(AVG(b.nivel_estresse), 2) AS media_estresse,
                ROUND(AVG(b.nivel_motivacao), 2) AS media_motivacao,
                ROUND(AVG(b.qualidade_sono), 2) AS media_sono
            FROM bem_estar b
            JOIN usuarios u ON u.id_usuario = b.id_usuario
            WHERE u.id_empresa = :id_empresa
            """,
            {'id_empresa': id_empresa},
        )
        colunas = [col[0].lower() for col in cursor.description]
        row = cursor.fetchone()
        return dict(zip(colunas, row)) if row else {}
    except Exception as e:
        return {'error': str(e)}


def consulta_trilhas_mais_utilizadas_empresa(
    cursor, id_empresa: int
) -> List[Dict[str, Any]]:
    """
    Consulta trilhas mais utilizadas na empresa.
    Retorna lista de dicts: [{nome_trilha, total_usuarios}, ...]
    """
    try:
        if not isinstance(id_empresa, int):
            raise ValidationError('ID da empresa inválido')
        cursor.execute(
            """
            SELECT 
                t.nome_trilha,
                COUNT(*) AS total_usuarios
            FROM usuario_trilha ut
            JOIN usuarios u ON ut.id_usuario = u.id_usuario
            JOIN trilhas t ON t.id_trilha = ut.id_trilha
            WHERE u.id_empresa = :id_empresa
            GROUP BY t.nome_trilha
            ORDER BY total_usuarios DESC
            """,
            {'id_empresa': id_empresa},
        )
        colunas = [col[0].lower() for col in cursor.description]
        return [dict(zip(colunas, linha)) for linha in cursor.fetchall()]
    except Exception as e:
        return [{'error': str(e)}]


def consulta_funcionarios_baixa_motivacao(
    cursor, id_empresa: int
) -> List[Dict[str, Any]]:
    """
    Consulta funcionários com baixa motivação (<5).
    Retorna lista de dicts: [{nome_completo, nivel_motivacao, data_registro}, ...]
    """
    try:
        if not isinstance(id_empresa, int):
            raise ValidationError('ID da empresa inválido')
        cursor.execute(
            """
            SELECT 
                u.nome_completo,
                b.nivel_motivacao,
                b.data_registro
            FROM bem_estar b
            JOIN usuarios u ON u.id_usuario = b.id_usuario
            WHERE u.id_empresa = :id_empresa
              AND b.nivel_motivacao < 5
            ORDER BY b.data_registro DESC
            """,
            {'id_empresa': id_empresa},
        )
        colunas = [col[0].lower() for col in cursor.description]
        return [dict(zip(colunas, linha)) for linha in cursor.fetchall()]
    except Exception as e:
        return [{'error': str(e)}]
