"""
Utilitário para padronizar mensagens coloridas no terminal usando colorama.
"""

from colorama import Fore, Style, just_fix_windows_console

just_fix_windows_console()


class ColorMsg:
    MENU = Fore.CYAN + Style.BRIGHT
    TITLE = Fore.BLUE + Style.BRIGHT
    ERROR = Fore.RED + Style.BRIGHT
    SUCCESS = Fore.GREEN + Style.BRIGHT
    WARNING = Fore.YELLOW + Style.BRIGHT
    INPUT = Fore.MAGENTA + Style.NORMAL
    INFO = Fore.WHITE + Style.NORMAL
    RESET = Style.RESET_ALL

    @staticmethod
    def print_menu(msg):
        print(ColorMsg.MENU + msg + ColorMsg.RESET)

    @staticmethod
    def print_title(msg):
        print(ColorMsg.TITLE + msg + ColorMsg.RESET)

    @staticmethod
    def print_error(msg):
        print(ColorMsg.ERROR + msg + ColorMsg.RESET)

    @staticmethod
    def print_success(msg):
        print(ColorMsg.SUCCESS + msg + ColorMsg.RESET)

    @staticmethod
    def print_warning(msg):
        print(ColorMsg.WARNING + msg + ColorMsg.RESET)

    @staticmethod
    def print_info(msg):
        print(ColorMsg.INFO + msg + ColorMsg.RESET)

    @staticmethod
    def input_prompt(msg):
        return input(ColorMsg.INPUT + msg + ColorMsg.RESET)
