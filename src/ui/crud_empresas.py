"""
CRUD de empresas removido

Este arquivo era responsável pelo CRUD de empresas na interface.
O CRUD de empresas foi removido por solicitação e a navegação principal
não referencia mais este módulo. Mantemos este stub para evitar erros
caso alguma importação residual exista em versões antigas.
"""


def menu_empresas():
    raise RuntimeError(
        'CRUD de empresas foi removido. Use funcionalidades de usuários e consultas.'
    )


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
            ColorMsg.input_prompt('CNPJ: ').strip(),
            'CNPJ',
            max_length=MAX_CNPJ,
            required=True,
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

        # Verifica duplicidade de CNPJ ou email
        try:
            if db.cnpj_ou_email_existe(cnpj=cnpj, email_contato=email):
                ColorMsg.print_error('✗ CNPJ ou email já cadastrado.')
                return
        except DatabaseError as e:
            ColorMsg.print_warning(f'⚠ Não foi possível verificar duplicidade: {e}')

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
        id_empresa, err = validate_id(
            ColorMsg.input_prompt('\nID da empresa: ').strip(), 'ID'
        )
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
            ColorMsg.input_prompt('Novo CNPJ (vazio para manter): ').strip()
            or empresa.get('cnpj'),
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

        # Verifica duplicidade (exclui o próprio id)
        try:
            if db.cnpj_ou_email_existe(
                cnpj=cnpj, email_contato=email, exclude_id=id_empresa
            ):
                ColorMsg.print_error('✗ CNPJ ou email já utilizado por outra empresa.')
                return
        except DatabaseError as e:
            ColorMsg.print_warning(f'⚠ Não foi possível verificar duplicidade: {e}')

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
        confirm = ColorMsg.input_prompt(
            f"\n⚠ Confirma exclusão de '{nome}'? (s/n): "
        ).strip()
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
