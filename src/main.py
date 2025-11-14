"""
main.py

Ponto de entrada principal do sistema UpPath CRUD.
Inicializa o banco de dados e pool de conexões antes de exibir o menu.
"""

from pathlib import Path

# Carrega variáveis de ambiente do arquivo .env ANTES de importar módulos
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Agora importa os módulos que dependem das variáveis de ambiente
from services import storage_oracle as db
from ui import crud_usuarios


def querries():    
    """Função para exibir querries disponíveis."""
    print('\n' + '=' * 60)
    print('QUERRIES DISPONÍVEIS')
    print('=' * 60)
    print('1 - Listar usuários por faixa etária')
    print('2 - Contar usuários por Genero')
    print('3 - Listar usuários criados em um período específico')
    print('0 - Voltar ao menu principal')
    print('=' * 60)

    opcao = input('Escolha uma opção de querry: ').strip()

    if opcao == '1':
        crud_usuarios.listar_usuarios_faixa_etaria()
    elif opcao == '2':
        crud_usuarios.contar_usuarios_genero()
    elif opcao == '3':
        crud_usuarios.listar_usuarios_periodo_criacao()
    elif opcao == '0':
        return

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

        # Operando sem pool de conexões (conexões diretas)

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
        print('6 - Querries')
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
        elif opcao == '6':
            crud_usuarios.querries()
        elif opcao == '0':
            print('\nEncerrando sistema...')
            break


if __name__ == '__main__':
    main()
