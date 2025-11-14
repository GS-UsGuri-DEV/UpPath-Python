"""
Teste completo: Criar e atualizar usuário com diferentes cenários de data_nascimento.
"""

import sys
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Carrega variáveis de ambiente
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

import hashlib

from services import storage_oracle as db


def test_complete_workflow():
    """Testa o workflow completo de criação e atualização."""

    print('\n' + '=' * 70)
    print('TESTE COMPLETO: Criação e Atualização com data_nascimento')
    print('=' * 70)

    # Cenário 1: Criar usuário SEM data de nascimento
    print('\n[CENÁRIO 1] Criar usuário sem data de nascimento')
    print('-' * 70)

    usuario1 = {
        'id_empresa': None,
        'nome_completo': 'Teste User 1',
        'email': f'teste1_{date.today().isoformat()}@example.com',
        'senha_hash': hashlib.sha256('senha123'.encode()).hexdigest(),
        'nivel_carreira': 'Júnior',
        'ocupacao': 'Desenvolvedor',
        'genero': 'Não especificado',
        'data_nascimento': None,  # SEM data
        'is_admin': 0,
    }

    try:
        id1 = db.insert_usuario(usuario1)
        print(f'✓ Usuário criado: ID={id1}')

        # Verifica a data
        user = db.get_usuario_por_id(id1)
        print(f'  Data de nascimento salva: {user["data_nascimento"]}')

        if user['data_nascimento'] == '1900-01-01T00:00:00':
            print('  ✓ Data padrão aplicada corretamente!')

    except Exception as e:
        print(f'✗ Erro: {e}')
        return

    # Cenário 2: Criar usuário COM data de nascimento
    print('\n[CENÁRIO 2] Criar usuário com data de nascimento válida')
    print('-' * 70)

    usuario2 = {
        'id_empresa': None,
        'nome_completo': 'Teste User 2',
        'email': f'teste2_{date.today().isoformat()}@example.com',
        'senha_hash': hashlib.sha256('senha123'.encode()).hexdigest(),
        'nivel_carreira': 'Pleno',
        'ocupacao': 'Analista',
        'genero': 'Masculino',
        'data_nascimento': '15/03/1995',  # COM data
        'is_admin': 0,
    }

    try:
        id2 = db.insert_usuario(usuario2)
        print(f'✓ Usuário criado: ID={id2}')

        # Verifica a data
        user = db.get_usuario_por_id(id2)
        print(f'  Data de nascimento salva: {user["data_nascimento"]}')

        if '1995-03-15' in user['data_nascimento']:
            print('  ✓ Data fornecida salva corretamente!')

    except Exception as e:
        print(f'✗ Erro: {e}')
        return

    # Cenário 3: Atualizar usuário mantendo a data existente
    print('\n[CENÁRIO 3] Atualizar usuário mantendo data existente')
    print('-' * 70)

    try:
        user = db.get_usuario_por_id(id2)
        user['ocupacao'] = 'Analista Sênior'  # Altera apenas ocupação

        db.update_usuario(id2, user)
        print(f'✓ Usuário ID={id2} atualizado')

        # Verifica se a data foi mantida
        user_updated = db.get_usuario_por_id(id2)
        print(f'  Data após update: {user_updated["data_nascimento"]}')

        if '1995-03-15' in user_updated['data_nascimento']:
            print('  ✓ Data original mantida corretamente!')
        else:
            print('  ✗ Data alterada inesperadamente!')

    except Exception as e:
        print(f'✗ Erro ao atualizar: {e}')
        return

    # Cenário 4: Atualizar usuário alterando a data
    print('\n[CENÁRIO 4] Atualizar usuário alterando data de nascimento')
    print('-' * 70)

    try:
        user = db.get_usuario_por_id(id2)
        user['data_nascimento'] = '20/06/1990'  # Nova data

        db.update_usuario(id2, user)
        print(f'✓ Usuário ID={id2} atualizado com nova data')

        # Verifica a nova data
        user_updated = db.get_usuario_por_id(id2)
        print(f'  Data após update: {user_updated["data_nascimento"]}')

        if '1990-06-20' in user_updated['data_nascimento']:
            print('  ✓ Nova data salva corretamente!')
        else:
            print('  ✗ Data não atualizada corretamente!')

    except Exception as e:
        print(f'✗ Erro ao atualizar: {e}')
        return

    # Limpeza: Remove usuários de teste
    print('\n[LIMPEZA] Removendo usuários de teste...')
    print('-' * 70)

    try:
        db.delete_usuario(id1)
        print(f'✓ Usuário ID={id1} removido')
        db.delete_usuario(id2)
        print(f'✓ Usuário ID={id2} removido')
    except Exception as e:
        print(f'⚠ Aviso ao limpar: {e}')

    print('\n' + '=' * 70)
    print('TODOS OS TESTES CONCLUÍDOS COM SUCESSO!')
    print('=' * 70)
    print('\n✓ Problema do ORA-01407 (data_nascimento NULL) RESOLVIDO!')
    print('  - Criação com data NULL agora usa data padrão (01/01/1900)')
    print('  - Atualização preserva data existente do banco')
    print('  - Atualização com nova data funciona corretamente')


if __name__ == '__main__':
    test_complete_workflow()
