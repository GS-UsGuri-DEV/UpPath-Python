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


def _pretty_print(data):
    """Imprime de forma amigável estruturas retornadas pelas consultas.

    - Lista de dicts -> tabela
    - Dict -> chaves: valores
    - Lista de valores simples -> linhas enumeradas
    """
    if data is None:
        ColorMsg.print_warning('Nenhum dado retornado.')
        return

    # Lista vazia
    if isinstance(data, list) and len(data) == 0:
        ColorMsg.print_warning('Nenhum registro encontrado.')
        return

    # Lista de dicionários -> tabela
    if isinstance(data, list) and all(isinstance(d, dict) for d in data):
        # coletar colunas como união de chaves (mantendo ordem aparente)
        cols = []
        for row in data:
            for k in row.keys():
                if k not in cols:
                    cols.append(k)

        def fmt_value(v):
            if v is None:
                return ''
            # datetime -> iso
            if isinstance(v, (datetime.datetime, datetime.date)):
                return v.isoformat()
            return str(v)

        # determinar larguras e tipos (numérico ou não)
        widths = {c: len(c) for c in cols}
        is_numeric = {c: True for c in cols}
        for row in data:
            for c in cols:
                s = fmt_value(row.get(c, ''))
                widths[c] = max(widths[c], len(s))
                # checar se ainda pode ser numérico
                if s == '':
                    continue
                try:
                    float(s)
                except Exception:
                    is_numeric[c] = False

        # cabeçalho
        header_parts = []
        for c in cols:
            header_parts.append(
                c.rjust(widths[c]) if is_numeric[c] else c.ljust(widths[c])
            )
        header = ' | '.join(header_parts)
        sep = '-+-'.join('-' * widths[c] for c in cols)
        ColorMsg.print_info(header)
        ColorMsg.print_info(sep)

        for row in data:
            parts = []
            for c in cols:
                s = fmt_value(row.get(c, ''))
                if is_numeric[c]:
                    parts.append(s.rjust(widths[c]))
                else:
                    parts.append(s.ljust(widths[c]))
            ColorMsg.print_info(' | '.join(parts))
        return

    # Dicionário simples
    if isinstance(data, dict):
        for k, v in data.items():
            ColorMsg.print_info(f'{k}: {v}')
        return

    # Lista de valores simples
    if isinstance(data, list):
        for i, v in enumerate(data, 1):
            ColorMsg.print_info(f'{i}. {v}')
        return

    # Fallback
    ColorMsg.print_info(str(data))


def querries():
    """Menu de consultas customizadas, incluindo dashboards."""
    ColorMsg.print_menu('\n' + '=' * 60)
    ColorMsg.print_menu('CONSULTAS E DASHBOARDS')
    ColorMsg.print_menu('=' * 60)
    ColorMsg.print_menu('1 - Painel individual (usuário)')
    ColorMsg.print_menu('2 - Painel corporativo (empresa)')
    ColorMsg.print_menu('3 - Empresas (contagem de funcionários)')
    ColorMsg.print_menu('0 - Voltar ao menu principal')
    ColorMsg.print_menu('=' * 60)
    opcao = ColorMsg.input_prompt('Escolha uma opção: ').strip()
    if opcao == '1':
        querries_usuario()
    elif opcao == '2':
        painel_corporativo()
    elif opcao == '3':
        # Consulta read-only: lista de empresas com contagem de funcionários
        with db.get_cursor() as cursor:
            dados = consultas.consulta_empresas_com_contagem(cursor)
            _pretty_print(dados)
            export = (
                ColorMsg.input_prompt('Exportar resultado para JSON? (s/n): ')
                .strip()
                .lower()
            )
            if export in ('s', 'sim', 'y', 'yes'):
                nome_arquivo = ColorMsg.input_prompt(
                    'Nome do arquivo (ex: empresas_contagem.json): '
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
        _pretty_print(dados)
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
        _pretty_print(dados)
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
