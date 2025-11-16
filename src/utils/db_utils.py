"""
Utilitários para gerenciamento de banco de dados.
"""

import logging
from contextlib import contextmanager
from datetime import date, datetime
from typing import Any, Dict, List, Optional

from src.services import DAO as db


@contextmanager
def get_db_connection(conn_info: Dict = None):
    """Context manager para gerenciar conexões do banco de dados.

    Usage:
        with get_db_connection() as conn:
            cur = conn.cursor()
            # ... operações
    """
    conn = None
    try:
        conn = db._connect(conn_info)
        yield conn
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        logging.error(f'Erro na operação do banco: {e}')
        raise
    finally:
        if conn:
            conn.close()


def parse_date_for_db(date_input: Any) -> Optional[date]:
    """Converte diversos formatos de data para objeto date.

    Args:
        date_input: str (YYYY-MM-DD), date, datetime, ou None

    Returns:
        date object ou None
    """
    if date_input is None:
        return None

    if isinstance(date_input, date):
        return date_input

    if isinstance(date_input, datetime):
        return date_input.date()

    if isinstance(date_input, str):
        try:
            return datetime.strptime(date_input, '%Y-%m-%d').date()
        except ValueError:
            logging.warning(f'Data inválida: {date_input}')
            return None

    return None


def rows_to_dicts(cursor) -> List[Dict]:
    """Converte resultados de cursor Oracle em lista de dicionários.

    Args:
        cursor: Cursor Oracle com resultados

    Returns:
        Lista de dicionários com chaves em lowercase
    """
    if not cursor.description:
        return []

    cols = [c[0].lower() for c in cursor.description]
    rows = cursor.fetchall()
    results = []

    for row in rows:
        d = {}
        for col, val in zip(cols, row):
            if isinstance(val, (date, datetime)):
                try:
                    d[col] = val.isoformat()
                except Exception:
                    d[col] = str(val)
            else:
                d[col] = val
        results.append(d)

    return results


def format_usuario_display(usuario: Dict) -> str:
    """Formata usuário para exibição amigável.

    Args:
        usuario: Dicionário com dados do usuário

    Returns:
        String formatada para display
    """
    return (
        f'ID: {usuario.get("id_usuario", "N/A")} | '
        f'Nome: {usuario.get("nome_completo", "N/A")} | '
        f'Email: {usuario.get("email", "N/A")} | '
        f'Empresa: {usuario.get("id_empresa") or "N/A"} | '
        f'Nível: {usuario.get("nivel_carreira", "N/A")} | '
        f'Ocupação: {usuario.get("ocupacao", "N/A")} | '
        f'Gênero: {usuario.get("genero", "N/A")} | '
        f'Nasc: {usuario.get("data_nascimento") or "N/A"} | '
        f'Admin: {"Sim" if usuario.get("is_admin") == 1 else "Não"}'
    )


def apply_defaults_to_usuario(usuario: Dict) -> Dict:
    """Aplica valores default para campos obrigatórios de usuário.

    Args:
        usuario: Dicionário de usuário (modificado in-place)

    Returns:
        Dicionário de usuário com defaults aplicados
    """
    defaults = {
        'nivel_carreira': 'Não especificado',
        'ocupacao': 'Não especificado',
        'genero': 'Não especificado',
        'is_admin': 0,
    }

    for key, default_value in defaults.items():
        if not usuario.get(key):
            usuario[key] = default_value

    return usuario
