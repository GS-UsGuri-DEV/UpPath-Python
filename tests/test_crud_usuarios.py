import builtins

import pytest

from ui import crud_usuarios


class DummyDB:
    def __init__(self):
        self.insert_called_with = None

    def email_existe(self, email, exclude_id=None):
        # Simula inexistência de email
        return False

    def insert_usuario(self, usuario):
        # Armazena o dict recebido para asserções e devolve um id fictício
        self.insert_called_with = usuario
        return 123


def test_criar_usuario_passa_email_string(monkeypatch, capsys):
    """Garante que o email passado para insert_usuario é a string válida."""
    dummy = DummyDB()

    # Substitui o DB usado pelo módulo UI pelo dummy
    monkeypatch.setattr(crud_usuarios, 'db', dummy)

    # Sequência de entradas simuladas conforme as chamadas de input() em criar_usuario()
    inputs = [
        '',  # ID da empresa (opcional)
        'Test User',  # Nome completo
        'test@example.com',  # Email
        'password123',  # Senha
        '',  # Nível de carreira (enter para default)
        '',  # Ocupação
        '',  # Gênero
        '',  # Data de nascimento
        'n',  # É administrador? (s/n)
    ]

    def fake_input(prompt=''):
        # Retorna a próxima entrada simulada
        try:
            return inputs.pop(0)
        except IndexError:
            pytest.fail('Chamadas a input() excederam entradas simuladas')

    monkeypatch.setattr(builtins, 'input', fake_input)

    # Executa a função (não usamos um Oracle real)
    crud_usuarios.criar_usuario()

    # Verificações
    assert dummy.insert_called_with is not None, 'insert_usuario não foi chamado'
    received_email = dummy.insert_called_with.get('email')
    assert isinstance(received_email, str), (
        f'Email deveria ser str, foi {type(received_email)}'
    )
    assert received_email == 'test@example.com'

    # Verifica saída para confirmar fluxo de sucesso
    captured = capsys.readouterr()
    assert (
        'Usuário cadastrado com sucesso' in captured.out
        or 'Erro ao inserir usuário' not in captured.out
    )
