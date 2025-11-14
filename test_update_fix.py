"""
Script de teste para verificar a correção do problema de UPDATE com data_nascimento NULL.
"""

import sys
from pathlib import Path

from dotenv import load_dotenv

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Carrega variáveis de ambiente
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

from services import storage_oracle as db


def test_update_with_null_date():
    """Testa atualização de usuário com data_nascimento NULL."""

    print('\n' + '=' * 60)
    print('TESTE: Atualização com data_nascimento NULL')
    print('=' * 60)

    # Lista usuários existentes
    usuarios = db.list_usuarios()

    if not usuarios:
        print('\n✗ Nenhum usuário encontrado para testar.')
        print('  Crie um usuário primeiro usando o sistema.')
        return

    # Pega o primeiro usuário
    usuario_teste = usuarios[0]
    id_teste = usuario_teste['id_usuario']

    print(f'\n1. Usuário de teste: ID={id_teste}')
    print(f'   Nome: {usuario_teste["nome_completo"]}')
    print(f'   Data nascimento atual: {usuario_teste["data_nascimento"]}')

    # Simula uma atualização sem modificar a data
    print('\n2. Tentando atualizar sem modificar a data de nascimento...')

    try:
        # Carrega o usuário novamente
        usuario = db.get_usuario_por_id(id_teste)

        # Faz uma pequena alteração que não afeta a data
        # (simula o comportamento do menu de atualização)
        usuario['ocupacao'] = usuario.get('ocupacao', 'Não especificado')

        # Tenta atualizar
        db.update_usuario(id_teste, usuario)

        print('✓ Atualização realizada com sucesso!')

        # Verifica se a data foi mantida ou recebeu valor padrão
        usuario_atualizado = db.get_usuario_por_id(id_teste)
        print(f'\n3. Data após atualização: {usuario_atualizado["data_nascimento"]}')

        if usuario_atualizado['data_nascimento'] is None:
            print('   ⚠ Atenção: Data ainda está NULL (pode indicar problema)')
        elif usuario_atualizado['data_nascimento'] == '1900-01-01':
            print('   ✓ Data padrão aplicada: 01/01/1900')
        else:
            print('   ✓ Data mantida do banco original')

    except Exception as e:
        print(f'\n✗ ERRO ao atualizar: {e}')
        return

    print('\n' + '=' * 60)
    print('TESTE CONCLUÍDO')
    print('=' * 60)


if __name__ == '__main__':
    test_update_with_null_date()
