"""
validators.py

Módulo centralizado para validações reutilizáveis.
"""

import re
from datetime import date, datetime
from typing import Optional, Tuple

# Constantes de validação
MAX_NOME_COMPLETO = 60
MAX_EMAIL = 60
MAX_NIVEL_CARREIRA = 30
MAX_OCUPACAO = 30
MAX_GENERO = 15
MAX_CNPJ = 18

EMAIL_PATTERN = r'^[\w\.-]+@[\w\.-]+\.\w+$'
DATE_FORMAT = '%Y-%m-%d'


class ValidationError(Exception):
    """Exceção personalizada para erros de validação."""

    pass


def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """Valida formato e tamanho de email.

    Returns:
        (is_valid, error_message)
    """
    if not email:
        return False, 'Email não pode ser vazio'
    if len(email) > MAX_EMAIL:
        return False, f'Email muito longo (máximo {MAX_EMAIL} caracteres)'
    if not re.match(EMAIL_PATTERN, email):
        return False, 'Formato de email inválido'
    return True, None


def validate_string_field(
    value: str,
    field_name: str,
    max_length: int,
    required: bool = True,
    default: str = None,
) -> Tuple[str, Optional[str]]:
    """Valida campo de texto genérico.

    Returns:
        (validated_value, error_message)
    """
    if not value or not value.strip():
        if required and default is None:
            return None, f'{field_name} não pode ser vazio'
        return default or 'Não especificado', None

    value = value.strip()
    if len(value) > max_length:
        return None, f'{field_name} muito longo (máximo {max_length} caracteres)'

    return value, None


def validate_date(
    date_str: str, required: bool = False
) -> Tuple[Optional[date], Optional[str]]:
    """Valida e converte string de data.

    Returns:
        (date_object, error_message)
    """
    if not date_str or not date_str.strip():
        if required:
            return None, 'Data é obrigatória'
        return None, None

    try:
        return datetime.strptime(date_str, DATE_FORMAT).date(), None
    except ValueError:
        return None, f'Data inválida. Use o formato {DATE_FORMAT}'


def validate_id(
    id_str: str, field_name: str = 'ID'
) -> Tuple[Optional[int], Optional[str]]:
    """Valida string de ID numérico.

    Returns:
        (id_value, error_message)
    """
    if not id_str or not id_str.strip():
        return None, None

    if not id_str.isdigit():
        return None, f'{field_name} inválido (deve ser numérico)'

    return int(id_str), None


def validate_boolean_input(input_str: str, default: bool = False) -> bool:
    """Valida entrada sim/não.

    Returns:
        boolean value
    """
    if not input_str:
        return default
    return input_str.strip().lower() in ('s', 'sim', 'yes', 'y', '1', 'true')


def sanitize_for_db(value: str, max_length: int) -> str:
    """Sanitiza string para inserção no banco.

    Args:
        value: String a sanitizar
        max_length: Comprimento máximo

    Returns:
        String sanitizada
    """
    if not value:
        return ''

    # Remove espaços extras e limita tamanho
    sanitized = value.strip()[:max_length]
    return sanitized
