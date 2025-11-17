from src.services import empresa_dao as db
from src.services.exceptions import DatabaseError
from utils.validators import (
    MAX_CNPJ,
    validate_id,
    validate_string_field,
)


def menu_empresas():
    while True:
        print('\n' + '=' * 60)
        print('CRUD EMPRESAS')
        print('=' * 60)
        print('1 - Criar empresa')
        print('2 - Listar empresas')
        print('3 - Buscar empresa por ID')
        print('4 - Atualizar empresa')
        print('5 - Deletar empresa')
        print('0 - Voltar')
        print('=' * 60)
        opcao = input('Escolha: ').strip()
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
            print('✗ Opção inválida.')


def criar_empresa():
    try:
        print('\n' + '=' * 60)
        print('CADASTRO DE NOVA EMPRESA')
        print('=' * 60)

        nome, err = validate_string_field(
            input('Nome da empresa: ').strip(),
            'Nome empresa',
            max_length=60,
            required=True,
        )
        if err:
            print(f'✗ {err}')
            return

        cnpj, err = validate_string_field(
            input('CNPJ: ').strip(), 'CNPJ', max_length=MAX_CNPJ, required=True
        )
        if err:
            print(f'✗ {err}')
            return

        email, err = validate_string_field(
            input('Email de contato: ').strip(),
            'Email contato',
            max_length=60,
            required=True,
        )
        if err:
            print(f'✗ {err}')
            return

        empresa = {'nome_empresa': nome, 'cnpj': cnpj, 'email_contato': email}

        try:
            new_id = db.insert_empresa(empresa)
            print(f'\n✓ Empresa cadastrada com sucesso! ID: {new_id}')
        except DatabaseError as e:
            print(f'\n✗ Erro ao inserir empresa: {e}')
        except Exception as e:
            print(f'\n✗ Erro inesperado ao inserir empresa: {e}')

    except KeyboardInterrupt:
        print('\n\n✗ Operação cancelada pelo usuário.')
    except Exception as e:
        print(f'\n✗ Erro ao cadastrar empresa: {e}')


def listar_empresas():
    try:
        empresas = db.list_empresas()
        if not empresas:
            print('\n⚠ Nenhuma empresa cadastrada.')
            return
        print('\n' + '=' * 60)
        print(f'LISTA DE EMPRESAS ({len(empresas)} cadastrada(s))')
        print('=' * 60)
        for e in empresas:
            print(
                f'ID: {e.get("id_empresa")} | Nome: {e.get("nome_empresa")} | CNPJ: {e.get("cnpj")} | Email: {e.get("email_contato")}'
            )
    except Exception as e:
        print(f'\n✗ Erro ao listar empresas: {e}')


def buscar_empresa_por_id():
    try:
        id_empresa, err = validate_id(input('\nID da empresa: ').strip(), 'ID')
        if err or not id_empresa:
            return
        empresa = db.get_empresa_por_id(id_empresa)
        if not empresa:
            print(f'\n✗ Empresa com ID {id_empresa} não encontrada.')
            return
        print('\n' + '=' * 60)
        print('DADOS DA EMPRESA')
        print('=' * 60)
        print(f'ID: {empresa.get("id_empresa")}')
        print(f'Nome: {empresa.get("nome_empresa")}')
        print(f'CNPJ: {empresa.get("cnpj")}')
        print(f'Email contato: {empresa.get("email_contato")}')
        print(f'Cadastrada em: {empresa.get("data_cadastro")}')
    except Exception as e:
        print(f'\n✗ Erro ao buscar empresa: {e}')


def atualizar_empresa():
    try:
        id_empresa, err = validate_id(
            input('\nID da empresa a atualizar: ').strip(), 'ID'
        )
        if err or not id_empresa:
            return
        empresa = db.get_empresa_por_id(id_empresa)
        if not empresa:
            print('\n✗ Empresa não encontrada.')
            return

        nome, _ = validate_string_field(
            input('Novo nome (vazio para manter): ').strip()
            or empresa.get('nome_empresa'),
            'Nome empresa',
            max_length=60,
            required=True,
        )
        cnpj, _ = validate_string_field(
            input('Novo CNPJ (vazio para manter): ').strip() or empresa.get('cnpj'),
            'CNPJ',
            max_length=MAX_CNPJ,
            required=True,
        )
        email, _ = validate_string_field(
            input('Novo email contato (vazio para manter): ').strip()
            or empresa.get('email_contato'),
            'Email contato',
            max_length=60,
            required=True,
        )

        novo = {'nome_empresa': nome, 'cnpj': cnpj, 'email_contato': email}
        try:
            db.update_empresa(id_empresa, novo)
            print('\n✓ Empresa atualizada com sucesso!')
        except DatabaseError as e:
            print(f'\n✗ Erro ao atualizar empresa: {e}')
        except Exception as e:
            print(f'\n✗ Erro inesperado ao atualizar empresa: {e}')

    except Exception as e:
        print(f'\n✗ Erro ao atualizar empresa: {e}')


def deletar_empresa():
    try:
        id_empresa, err = validate_id(
            input('\nID da empresa a remover: ').strip(), 'ID'
        )
        if err or not id_empresa:
            return
        empresa = db.get_empresa_por_id(id_empresa)
        if not empresa:
            print('\n✗ Empresa não encontrada.')
            return
        nome = empresa.get('nome_empresa')
        confirm = input(f"\n⚠ Confirma exclusão de '{nome}'? (s/n): ").strip()
        if confirm.lower() in ('s', 'sim', 'y', 'yes'):
            try:
                db.delete_empresa(id_empresa)
                print(f'\n✓ Empresa "{nome}" removida com sucesso!')
            except DatabaseError as e:
                print(f'\n✗ Erro ao remover empresa: {e}')
            except Exception as e:
                print(f'\n✗ Erro inesperado ao remover empresa: {e}')
        else:
            print('\n✗ Exclusão cancelada.')
    except Exception as e:
        print(f'\n✗ Erro ao deletar empresa: {e}')
