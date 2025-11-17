"""Exceções customizadas para a camada de serviços/DAO."""


class DatabaseError(Exception):
    """Erro genérico relacionado a operações com o banco de dados."""


class NotFoundError(Exception):
    """Entidade não encontrada."""


class ValidationError(Exception):
    """Erro de validação de dados de entrada."""
