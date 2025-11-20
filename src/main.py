"""
main.py

Ponto de entrada principal do sistema UpPath CRUD.
Inicializa o banco de dados antes de exibir o menu.
"""

import sys
from pathlib import Path

from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Garantir que a raiz do projeto esteja no sys.path para permitir
# imports absolutos do pacote `src` quando o script for executado
# diretamente (ex: `python src\\main.py`).
project_root = Path(__file__).parent.parent.resolve()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def main():
    """Função principal que inicializa o sistema e exibe o menu."""
    # agora que o .env foi carregado e o sys.path ajustado, importe os
    # módulos que dependem das variáveis de ambiente/projeto
    from src.services import DAO as db
    from src.ui import crud_usuarios, painel_queries
    from src.utils.color_msg import ColorMsg

    ColorMsg.print_title('=' * 60)
    ColorMsg.print_title('Sistema UpPath - Gestão de Usuários')
    ColorMsg.print_title('=' * 60)

    # Inicializa tabelas e sequence (executado apenas uma vez)
    try:
        ColorMsg.print_info('\nInicializando banco de dados...')
        db.init_table()
        ColorMsg.print_success('OK - Banco de dados inicializado com sucesso!')
    except Exception as e:
        ColorMsg.print_error(f'\nERRO ao inicializar banco de dados: {e}')
        ColorMsg.print_warning(
            'Verifique se as variáveis de ambiente estão configuradas:'
        )
        ColorMsg.print_warning('  - ORACLE_USER')
        ColorMsg.print_warning('  - ORACLE_PASSWORD')
        ColorMsg.print_warning('  - ORACLE_DSN')
        return

    # Menu principal
    while True:
        ColorMsg.print_menu('\n' + '=' * 60)
        ColorMsg.print_menu('MENU PRINCIPAL')
        ColorMsg.print_menu('=' * 60)
        ColorMsg.print_menu('1 - Criar usuário')
        ColorMsg.print_menu('2 - Listar usuários')
        ColorMsg.print_menu('3 - Buscar usuário por ID')
        ColorMsg.print_menu('4 - Atualizar usuário')
        ColorMsg.print_menu('5 - Deletar usuário')
        ColorMsg.print_menu('6 - Querries')
        ColorMsg.print_menu('0 - Sair')
        ColorMsg.print_menu('=' * 60)

        opcao = ColorMsg.input_prompt('Escolha uma opção: ').strip()

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
        elif opcao == '6':
            painel_queries.querries()
        elif opcao == '0':
            ColorMsg.print_info('\nEncerrando sistema...')
            break
        else:
            ColorMsg.print_error('✗ Opção inválida. Tente novamente.')


if __name__ == '__main__':
    main()
