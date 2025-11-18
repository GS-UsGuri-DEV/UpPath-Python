"""Centraliza configurações da aplicação (DB, etc.)."""

import os
from typing import Dict, Optional


def get_db_config() -> Optional[Dict[str, str]]:
    user = os.getenv('ORACLE_USER')
    password = os.getenv('ORACLE_PASSWORD')
    dsn = os.getenv('ORACLE_DSN')
    if not (user and password and dsn):
        return None
    return {'user': user, 'password': password, 'dsn': dsn}
