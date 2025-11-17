import json
from src.services import consultas
from src.services import DAO as db
from src.utils.validators import validate_id

def querries():
    """Menu de consultas customizadas, incluindo dashboards."""
    print('\n' + '=' * 60)
    print('CONSULTAS E DASHBOARDS')
    print('=' * 60)
    print('1 - Painel individual (usuário)')
    print('2 - Painel corporativo (empresa)')
    print('0 - Voltar ao menu principal')
    print('=' * 60)
    opcao = input('Escolha uma opção: ').strip()
    if opcao == '1':
        querries_usuario()
    elif opcao == '2':
        painel_corporativo()
    elif opcao == '0':
        return
    else:
        print('✗ Opção inválida.')

def painel_corporativo():
    """Menu para consultas do painel corporativo da empresa."""
    print('\n' + '=' * 60)
    print('PAINEL CORPORATIVO (Empresa)')
    print('=' * 60)
    print('1 - Distribuição de níveis de carreira')
    print('2 - Média de bem-estar da empresa')
    print('3 - Trilhas mais utilizadas')
    print('4 - Funcionários com baixa motivação (<5)')
    print('0 - Voltar')
    print('=' * 60)
    opcao = input('Escolha uma opção: ').strip()
    id_empresa_str = input('ID da empresa: ').strip()
    id_empresa, err = validate_id(id_empresa_str, 'ID da empresa')
    if err or id_empresa is None:
        print(f'✗ {err or "ID inválido"}')
        return
    with db.get_cursor() as cursor:
        if opcao == '1':
            dados = consultas.consulta_distribuicao_nivel_carreira(cursor, id_empresa)
        elif opcao == '2':
            dados = consultas.consulta_media_bem_estar_empresa(cursor, id_empresa)
        elif opcao == '3':
            dados = consultas.consulta_trilhas_mais_utilizadas_empresa(cursor, id_empresa)
        elif opcao == '4':
            dados = consultas.consulta_funcionarios_baixa_motivacao(cursor, id_empresa)
        elif opcao == '0':
            return
        else:
            print('✗ Opção inválida.')
            return
        print(json.dumps(dados, ensure_ascii=False, indent=2))
        export = input('Exportar resultado para JSON? (s/n): ').strip().lower()
        if export in ('s', 'sim', 'y', 'yes'):
            nome_arquivo = input('Nome do arquivo (ex: painel_empresa.json): ').strip()
            with open(nome_arquivo, 'w', encoding='utf-8') as f:
                json.dump(dados, f, ensure_ascii=False, indent=2)
            print(f'✓ Exportado para {nome_arquivo}')

def querries_usuario():
    """Menu para consultas do painel individual do usuário."""
    print('\n' + '=' * 60)
    print('PAINEL do Usuário)')
    print('=' * 60)
    print('1 - Evolução do bem-estar')
    print('2 - Progresso nas trilhas')
    print('3 - Recomendações recebidas')
    print('0 - Voltar')
    print('=' * 60)
    opcao = input('Escolha uma opção: ').strip()
    id_user_str = input('ID do usuário: ').strip()
    id_user, err = validate_id(id_user_str, 'ID do usuário')
    if err or id_user is None:
        print(f'✗ {err or "ID inválido"}')
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
            print('✗ Opção inválida.')
            return
        print(json.dumps(dados, ensure_ascii=False, indent=2))
        export = input('Exportar resultado para JSON? (s/n): ').strip().lower()
        if export in ('s', 'sim', 'y', 'yes'):
            nome_arquivo = input('Nome do arquivo (ex: painel_user.json): ').strip()
            with open(nome_arquivo, 'w', encoding='utf-8') as f:
                json.dump(dados, f, ensure_ascii=False, indent=2)
            print(f'✓ Exportado para {nome_arquivo}')
