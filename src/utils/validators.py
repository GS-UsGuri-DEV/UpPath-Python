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
DATE_FORMAT = '%d/%m/%Y'
DATE_FORMAT_ISO = '%Y-%m-%d'


class ValidationError(Exception):
    """Exceção personalizada para erros de validação."""

    pass


def validate_email(email: str) -> Tuple[Optional[str], Optional[str]]:
    """Valida formato e tamanho de email.

    Returns:
        (validated_email, error_message)
    """
    if not email or not email.strip():
        return None, 'Email não pode ser vazio'

    email = email.strip()

    if len(email) > MAX_EMAIL:
        return None, f'Email muito longo (máximo {MAX_EMAIL} caracteres)'
    if not re.match(EMAIL_PATTERN, email):
        return None, 'Formato de email inválido'
    return email, None


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

    Aceita por padrão o formato BR `DD/MM/YYYY`. Também aceita `YYYY-MM-DD`.

    Returns:
        (date_object, error_message)
    """
    if not date_str or not date_str.strip():
        if required:
            return None, 'Data é obrigatória'
        return None, None

    s = date_str.strip()
    # Tenta formato BR primeiro
    try:
        return datetime.strptime(s, DATE_FORMAT).date(), None
    except ValueError:
        pass

    # Tenta formato ISO
    try:
        return datetime.strptime(s, DATE_FORMAT_ISO).date(), None
    except ValueError:
        return None, f'Data inválida. Use o formato {DATE_FORMAT} (ex: 31/12/1990)'


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


def input_date_mask(prompt: str) -> str:
    """Lê uma data do usuário no formato DD/MM/YYYY com máscara de barras.

    Implementação leve compatível com Windows (usa `msvcrt`) e fallback
    para `input()` em outros sistemas.

    Retorna: string digitada (ex: '16/12/2002') ou '' se Enter sem digitar.
    """
    try:
        import msvcrt
    except Exception:
        return input(prompt)

    sys_stdout = __import__('sys').stdout

    buf = []
    positions = [2, 5]

    sys_stdout.write(prompt)
    sys_stdout.flush()

    while True:
        ch = msvcrt.getwch()
        if ch in ('\r', '\n'):
            sys_stdout.write('\n')
            return ''.join(buf)

        if ch in ('\x08',):
            if buf:
                buf.pop()
                if buf and len(buf) in positions and buf[-1] == '/':
                    buf.pop()
            sys_stdout.write('\r' + ' ' * (len(prompt) + 12) + '\r')
            sys_stdout.write(prompt + ''.join(buf))
            sys_stdout.flush()
            continue

        if not ch.isdigit():
            continue

        digits_only = [c for c in buf if c != '/']
        if len(digits_only) >= 8:
            continue

        digits_only.append(ch)
        new_buf = []
        for i, d in enumerate(digits_only):
            new_buf.append(d)
            if i + 1 in (2, 4) and i + 1 != len(digits_only):
                new_buf.append('/')

        buf = new_buf

        sys_stdout.write('\r' + ' ' * (len(prompt) + 12) + '\r')
        sys_stdout.write(prompt + ''.join(buf))
        sys_stdout.flush()
