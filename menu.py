# menu.py
# Menu interativo usando colorama
from colorama import Fore, init

init(autoreset=True)


def mostrar_menu_principal():
    print(Fore.CYAN + '===== MENU PRINCIPAL =====')
    print(Fore.YELLOW + '1 - Cadastrar Empresa')
    print(Fore.YELLOW + '2 - Listar Empresas')
    print(Fore.YELLOW + '3 - Atualizar Empresa')
    print(Fore.YELLOW + '4 - Remover Empresa')
    print(Fore.YELLOW + '5 - Cadastrar Usuário')
    print(Fore.YELLOW + '6 - Listar Usuários')
    print(Fore.YELLOW + '7 - Atualizar Usuário')
    print(Fore.YELLOW + '8 - Remover Usuário')
    print(Fore.YELLOW + '0 - Sair')
