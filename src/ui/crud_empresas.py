from src.services import empresa_dao as db
from src.services.exceptions import DatabaseError
from utils.validators import (
)
from src.utils.color_msg import ColorMsg
    MAX_CNPJ,
    validate_id,
    validate_string_field,
)


def menu_empresas():
    while True:
        ColorMsg.print_menu('\n' + '=' * 60)
        ColorMsg.print_menu('CRUD EMPRESAS')
        ColorMsg.print_menu('=' * 60)
        ColorMsg.print_menu('1 - Criar empresa')
        ColorMsg.print_menu('2 - Listar empresas')
        ColorMsg.print_menu('3 - Buscar empresa por ID')
        ColorMsg.print_menu('4 - Atualizar empresa')
        ColorMsg.print_menu('5 - Deletar empresa')
        ColorMsg.print_menu('0 - Voltar')
        ColorMsg.print_menu('=' * 60)
        opcao = ColorMsg.input_prompt('Escolha: ').strip()
        if opcao == '1':
            criar_empresa()
        elif opcao == '2':
            listar_empresas()
        elif opcao == '3':
            buscar_empresa_por_id()
        elif opcao == '4':
            atualizar_empresa()
        elif opcao == '5':
            deletar_empresa()
        elif opcao == '0':
            return
        else:
            ColorMsg.print_error('✗ Opção inválida.')


def criar_empresa():
    try:
        ColorMsg.print_title('\n' + '=' * 60)
        ColorMsg.print_title('CADASTRO DE NOVA EMPRESA')
        ColorMsg.print_title('=' * 60)

        nome, err = validate_string_field(
            ColorMsg.input_prompt('Nome da empresa: ').strip(),
            'Nome empresa',
            max_length=60,
            required=True,
        )
        if err:
            ColorMsg.print_error(f'✗ {err}')
            return

        cnpj, err = validate_string_field(
            ColorMsg.input_prompt('CNPJ: ').strip(), 'CNPJ', max_length=MAX_CNPJ, required=True
        )
        if err:
            ColorMsg.print_error(f'✗ {err}')
            return

        email, err = validate_string_field(
            ColorMsg.input_prompt('Email de contato: ').strip(),
            'Email contato',
            max_length=60,
            required=True,
        )
        if err:
            ColorMsg.print_error(f'✗ {err}')
            return

        empresa = {'nome_empresa': nome, 'cnpj': cnpj, 'email_contato': email}

        try:
            new_id = db.insert_empresa(empresa)
            ColorMsg.print_success(f'\n✓ Empresa cadastrada com sucesso! ID: {new_id}')
        except DatabaseError as e:
            ColorMsg.print_error(f'\n✗ Erro ao inserir empresa: {e}')
        except Exception as e:
            ColorMsg.print_error(f'\n✗ Erro inesperado ao inserir empresa: {e}')

    except KeyboardInterrupt:
        ColorMsg.print_warning('\n\n✗ Operação cancelada pelo usuário.')
    except Exception as e:
        ColorMsg.print_error(f'\n✗ Erro ao cadastrar empresa: {e}')


def listar_empresas():
    try:
        empresas = db.list_empresas()
        if not empresas:
            ColorMsg.print_warning('\n⚠ Nenhuma empresa cadastrada.')
            return
        ColorMsg.print_title('\n' + '=' * 60)
        ColorMsg.print_title(f'LISTA DE EMPRESAS ({len(empresas)} cadastrada(s))')
        ColorMsg.print_title('=' * 60)
        for e in empresas:
            ColorMsg.print_info(
                f'ID: {e.get("id_empresa")} | Nome: {e.get("nome_empresa")} | CNPJ: {e.get("cnpj")} | Email: {e.get("email_contato")}'
            )
    except Exception as e:
        ColorMsg.print_error(f'\n✗ Erro ao listar empresas: {e}')


def buscar_empresa_por_id():
    try:
        id_empresa, err = validate_id(ColorMsg.input_prompt('\nID da empresa: ').strip(), 'ID')
        if err or not id_empresa:
            return
        empresa = db.get_empresa_por_id(id_empresa)
        if not empresa:
            ColorMsg.print_error(f'\n✗ Empresa com ID {id_empresa} não encontrada.')
            return
        ColorMsg.print_title('\n' + '=' * 60)
        ColorMsg.print_title('DADOS DA EMPRESA')
        ColorMsg.print_title('=' * 60)
        ColorMsg.print_info(f'ID: {empresa.get("id_empresa")}')
        ColorMsg.print_info(f'Nome: {empresa.get("nome_empresa")}')
        ColorMsg.print_info(f'CNPJ: {empresa.get("cnpj")}')
        ColorMsg.print_info(f'Email contato: {empresa.get("email_contato")}')
        ColorMsg.print_info(f'Cadastrada em: {empresa.get("data_cadastro")}')
    except Exception as e:
        ColorMsg.print_error(f'\n✗ Erro ao buscar empresa: {e}')


def atualizar_empresa():
    try:
        id_empresa, err = validate_id(
            ColorMsg.input_prompt('\nID da empresa a atualizar: ').strip(), 'ID'
        )
        if err or not id_empresa:
            return
        empresa = db.get_empresa_por_id(id_empresa)
        if not empresa:
            ColorMsg.print_error('\n✗ Empresa não encontrada.')
            return

        nome, _ = validate_string_field(
            ColorMsg.input_prompt('Novo nome (vazio para manter): ').strip()
            or empresa.get('nome_empresa'),
            'Nome empresa',
            max_length=60,
            required=True,
        )
        cnpj, _ = validate_string_field(
            ColorMsg.input_prompt('Novo CNPJ (vazio para manter): ').strip() or empresa.get('cnpj'),
            'CNPJ',
            max_length=MAX_CNPJ,
            required=True,
        )
        email, _ = validate_string_field(
            ColorMsg.input_prompt('Novo email contato (vazio para manter): ').strip()
            or empresa.get('email_contato'),
            'Email contato',
            max_length=60,
            required=True,
        )

        novo = {'nome_empresa': nome, 'cnpj': cnpj, 'email_contato': email}
        try:
            db.update_empresa(id_empresa, novo)
            ColorMsg.print_success('\n✓ Empresa atualizada com sucesso!')
        except DatabaseError as e:
            ColorMsg.print_error(f'\n✗ Erro ao atualizar empresa: {e}')
        except Exception as e:
            ColorMsg.print_error(f'\n✗ Erro inesperado ao atualizar empresa: {e}')

    except Exception as e:
        ColorMsg.print_error(f'\n✗ Erro ao atualizar empresa: {e}')


def deletar_empresa():
    try:
        id_empresa, err = validate_id(
            ColorMsg.input_prompt('\nID da empresa a remover: ').strip(), 'ID'
        )
        if err or not id_empresa:
            return
        empresa = db.get_empresa_por_id(id_empresa)
        if not empresa:
            ColorMsg.print_error('\n✗ Empresa não encontrada.')
            return
        nome = empresa.get('nome_empresa')
        confirm = ColorMsg.input_prompt(f"\n⚠ Confirma exclusão de '{nome}'? (s/n): ").strip()
        if confirm.lower() in ('s', 'sim', 'y', 'yes'):
            try:
                db.delete_empresa(id_empresa)
                ColorMsg.print_success(f'\n✓ Empresa "{nome}" removida com sucesso!')
            except DatabaseError as e:
                ColorMsg.print_error(f'\n✗ Erro ao remover empresa: {e}')
            except Exception as e:
                ColorMsg.print_error(f'\n✗ Erro inesperado ao remover empresa: {e}')
        else:
            ColorMsg.print_warning('\n✗ Exclusão cancelada.')
    except Exception as e:
        ColorMsg.print_error(f'\n✗ Erro ao deletar empresa: {e}')
