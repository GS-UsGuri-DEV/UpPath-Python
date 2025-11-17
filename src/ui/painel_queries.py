import datetime
import json
import os

from src.services import DAO as db
from src.services import consultas
from src.utils.color_msg import ColorMsg
from src.utils.validators import validate_id


def _json_serializer(obj):
    """Serializador JSON para objetos não-serializáveis como datetime."""
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    # fallback: str() for other unknown types
    return str(obj)


def querries():
    """Menu de consultas customizadas, incluindo dashboards."""
    ColorMsg.print_menu('\n' + '=' * 60)
    ColorMsg.print_menu('CONSULTAS E DASHBOARDS')
    ColorMsg.print_menu('=' * 60)
    ColorMsg.print_menu('1 - Painel individual (usuário)')
    ColorMsg.print_menu('2 - Painel corporativo (empresa)')
    ColorMsg.print_menu('0 - Voltar ao menu principal')
    ColorMsg.print_menu('=' * 60)
    opcao = ColorMsg.input_prompt('Escolha uma opção: ').strip()
    if opcao == '1':
        querries_usuario()
    elif opcao == '2':
        painel_corporativo()
    elif opcao == '0':
        return
    else:
        ColorMsg.print_error('✗ Opção inválida.')


def painel_corporativo():
    """Menu para consultas do painel corporativo da empresa."""
    ColorMsg.print_menu('\n' + '=' * 60)
    ColorMsg.print_menu('PAINEL CORPORATIVO')
    ColorMsg.print_menu('=' * 60)
    ColorMsg.print_menu('1 - Distribuição de níveis de carreira')
    ColorMsg.print_menu('2 - Média de bem-estar da empresa')
    ColorMsg.print_menu('3 - Trilhas mais utilizadas')
    ColorMsg.print_menu('4 - Funcionários com baixa motivação (<5)')
    ColorMsg.print_menu('0 - Voltar')
    ColorMsg.print_menu('=' * 60)
    opcao = ColorMsg.input_prompt('Escolha uma opção: ').strip()
    id_empresa_str = ColorMsg.input_prompt('ID da empresa: ').strip()
    id_empresa, err = validate_id(id_empresa_str, 'ID da empresa')
    if err or id_empresa is None:
        ColorMsg.print_error(f'✗ {err or "ID inválido"}')
        return
    with db.get_cursor() as cursor:
        if opcao == '1':
            dados = consultas.consulta_distribuicao_nivel_carreira(cursor, id_empresa)
        elif opcao == '2':
            dados = consultas.consulta_media_bem_estar_empresa(cursor, id_empresa)
        elif opcao == '3':
            dados = consultas.consulta_trilhas_mais_utilizadas_empresa(
                cursor, id_empresa
            )
        elif opcao == '4':
            dados = consultas.consulta_funcionarios_baixa_motivacao(cursor, id_empresa)
        elif opcao == '0':
            return
        else:
            ColorMsg.print_error('✗ Opção inválida.')
            return
        ColorMsg.print_info(
            json.dumps(dados, ensure_ascii=False, indent=2, default=_json_serializer)
        )
        export = (
            ColorMsg.input_prompt('Exportar resultado para JSON? (s/n): ')
            .strip()
            .lower()
        )
        if export in ('s', 'sim', 'y', 'yes'):
            nome_arquivo = ColorMsg.input_prompt(
                'Nome do arquivo (ex: painel_empresa.json): '
            ).strip()
            pasta_data = os.path.join(os.path.dirname(__file__), '..', 'data')
            pasta_data = os.path.abspath(pasta_data)
            os.makedirs(pasta_data, exist_ok=True)
            caminho_arquivo = os.path.join(pasta_data, nome_arquivo)
            with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                json.dump(
                    dados, f, ensure_ascii=False, indent=2, default=_json_serializer
                )
            ColorMsg.print_success(f'✓ Exportado para {caminho_arquivo}')


def querries_usuario():
    """Menu para consultas do painel individual do usuário."""
    ColorMsg.print_menu('\n' + '=' * 60)
    ColorMsg.print_menu('PAINEL do Usuário')
    ColorMsg.print_menu('=' * 60)
    ColorMsg.print_menu('1 - Evolução do bem-estar')
    ColorMsg.print_menu('2 - Progresso nas trilhas')
    ColorMsg.print_menu('3 - Recomendações recebidas')
    ColorMsg.print_menu('0 - Voltar')
    ColorMsg.print_menu('=' * 60)
    opcao = ColorMsg.input_prompt('Escolha uma opção: ').strip()
    id_user_str = ColorMsg.input_prompt('ID do usuário: ').strip()
    id_user, err = validate_id(id_user_str, 'ID do usuário')
    if err or id_user is None:
        ColorMsg.print_error(f'✗ {err or "ID inválido"}')
        return
    with db.get_cursor() as cursor:
        if opcao == '1':
            dados = consultas.consulta_bem_estar_user(cursor, id_user)
        elif opcao == '2':
            dados = consultas.consulta_progresso_trilhas_user(cursor, id_user)
        elif opcao == '3':
            dados = consultas.consulta_recomendacoes_user(cursor, id_user)
        elif opcao == '0':
            return
        else:
            ColorMsg.print_error('✗ Opção inválida.')
            return
        ColorMsg.print_info(
            json.dumps(dados, ensure_ascii=False, indent=2, default=_json_serializer)
        )
        export = (
            ColorMsg.input_prompt('Exportar resultado para JSON? (s/n): ')
            .strip()
            .lower()
        )
        if export in ('s', 'sim', 'y', 'yes'):
            nome_arquivo = ColorMsg.input_prompt(
                'Nome do arquivo (ex: painel_user.json): '
            ).strip()
            pasta_data = os.path.join(os.path.dirname(__file__), '..', 'data')
            pasta_data = os.path.abspath(pasta_data)
            os.makedirs(pasta_data, exist_ok=True)
            caminho_arquivo = os.path.join(pasta_data, nome_arquivo)
            with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                json.dump(
                    dados, f, ensure_ascii=False, indent=2, default=_json_serializer
                )
            ColorMsg.print_success(f'✓ Exportado para {caminho_arquivo}')
