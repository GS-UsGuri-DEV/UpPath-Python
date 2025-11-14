"""
main.py

Ponto de entrada principal do sistema UpPath CRUD.
Inicializa o banco de dados e pool de conexões antes de exibir o menu.
"""

import logging
import sys
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from services import storage_oracle as db
from ui import crud_usuarios


def main():
    """Função principal que inicializa o sistema e exibe o menu."""
    print('=' * 60)
    print('Sistema UpPath - Gestão de Usuários')
    print('=' * 60)

    # Inicializa tabelas e sequence (executado apenas uma vez)
    try:
        print('\nInicializando banco de dados...')
        db.init_table()
        print('✓ Banco de dados inicializado com sucesso!')

        # Opcional: inicializar pool de conexões para melhor performance
        try:
            db.init_pool(min_connections=2, max_connections=5)
            print('✓ Pool de conexões inicializado!')
        except Exception as e:
            logging.warning(f'Pool de conexões não disponível: {e}')
            print('⚠ Operando sem pool de conexões (modo direto).')

    except Exception as e:
        print(f'\n✗ Erro ao inicializar banco de dados: {e}')
        print('Verifique se as variáveis de ambiente estão configuradas:')
        print('  - ORACLE_USER')
        print('  - ORACLE_PASSWORD')
        print('  - ORACLE_DSN')
        return

    # Menu principal
    while True:
        print('\n' + '=' * 60)
        print('MENU PRINCIPAL')
        print('=' * 60)
        print('1 - Criar usuário')
        print('2 - Listar usuários')
        print('3 - Buscar usuário por ID')
        print('4 - Atualizar usuário')
        print('5 - Deletar usuário')
        print('0 - Sair')
        print('=' * 60)

        opcao = input('Escolha uma opção: ').strip()

        if opcao == '1':
            crud_usuarios.criar_usuario()
        elif opcao == '2':
            crud_usuarios.listar_usuarios()
        elif opcao == '3':
            crud_usuarios.buscar_usuario_por_id()
        elif opcao == '4':
            crud_usuarios.atualizar_usuario()
        elif opcao == '5':
            crud_usuarios.deletar_usuario()
        elif opcao == '0':
            print('\nEncerrando sistema...')
            print('Até logo!')
            break
        else:
            print('\n✗ Opção inválida. Tente novamente.')


if __name__ == '__main__':
    main()
