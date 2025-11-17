import hashlib

from src.services import usuario_dao as db
from src.services.exceptions import DatabaseError
from src.utils.color_msg import ColorMsg
from src.utils.db_utils import format_usuario_display
from src.utils.validators import (
    MAX_GENERO,
    MAX_NIVEL_CARREIRA,
    MAX_NOME_COMPLETO,
    MAX_OCUPACAO,
    input_date_mask,
    validate_boolean_input,
    validate_date,
    validate_email,
    validate_id,
    validate_string_field,
)


def _input_with_validation(prompt: str, validator_func, **kwargs):
    """Helper genérico para input com validação.

    Args:
        prompt: Mensagem para o usuário
        validator_func: Função de validação (deve retornar (valor, erro))
        **kwargs: Argumentos adicionais para a função validadora

    Returns:
        Tupla (valor_validado, sucesso)
    """
    user_input = ColorMsg.input_prompt(prompt).strip()
    value, error = validator_func(user_input, **kwargs)

    if error:
        ColorMsg.print_error(f'✗ {error}')
        return None, False
    return value, True


def criar_usuario():
    """Cria um novo usuário com validações completas."""
    try:
        if db is None:
            ColorMsg.print_error('✗ Adaptador Oracle não disponível.')
            return

        ColorMsg.print_title('\n' + '=' * 60)
        ColorMsg.print_title('CADASTRO DE NOVO USUÁRIO')
        ColorMsg.print_title('=' * 60)

        # ID da empresa (opcional)
        id_empresa_str = ColorMsg.input_prompt(
            'ID da empresa (opcional, Enter para pular): '
        ).strip()
        id_empresa, id_empresa_error = validate_id(id_empresa_str, 'ID da empresa')
        if id_empresa_error or id_empresa is None:
            id_empresa = None

        # Nome completo
        nome_completo, success = _input_with_validation(
            'Nome completo: ',
            validate_string_field,
            field_name='Nome completo',
            max_length=MAX_NOME_COMPLETO,
            required=True,
        )
        if not success:
            return

        # Email
        email, success = _input_with_validation('Email: ', validate_email)
        if not success:
            return

        # Verifica duplicidade de email
        if db.email_existe(email):
            ColorMsg.print_error('✗ Email já cadastrado.')
            return

        # Senha
        senha = ColorMsg.input_prompt('Senha: ').strip()
        if not senha:
            ColorMsg.print_error('✗ Senha não pode ser vazia.')
            return
        senha_hash = hashlib.sha256(senha.encode('utf-8')).hexdigest()

        # Nível de carreira
        nivel_carreira, _ = _input_with_validation(
            'Nível de carreira (Júnior/Pleno/Sênior): ',
            validate_string_field,
            field_name='Nível de carreira',
            max_length=MAX_NIVEL_CARREIRA,
            required=False,
            default='Não especificado',
        )

        # Ocupação
        ocupacao, _ = _input_with_validation(
            'Ocupação (cargo): ',
            validate_string_field,
            field_name='Ocupação',
            max_length=MAX_OCUPACAO,
            required=False,
            default='Não especificado',
        )

        # Gênero
        genero, _ = _input_with_validation(
            'Gênero: ',
            validate_string_field,
            field_name='Gênero',
            max_length=MAX_GENERO,
            required=False,
            default='Não especificado',
        )

        # Data de nascimento (mascara BR DD/MM/YYYY)
        while True:
            dn_input = input_date_mask(
                ColorMsg.INPUT
                + 'Data de nascimento (DD/MM/YYYY, opcional): '
                + ColorMsg.RESET
            ).strip()
            dn_val, dn_err = validate_date(dn_input, required=False)
            if dn_err:
                ColorMsg.print_error(f'✗ {dn_err}')
                continue
            data_nascimento = dn_val
            break

        # Administrador
        is_admin_input = ColorMsg.input_prompt('É administrador? (s/n) [n]: ').strip()
        is_admin = 1 if validate_boolean_input(is_admin_input) else 0

        # Monta dicionário
        usuario = {
            'id_empresa': id_empresa,
            'nome_completo': nome_completo,
            'email': email,
            'senha_hash': senha_hash,
            'nivel_carreira': nivel_carreira,
            'ocupacao': ocupacao,
            'genero': genero,
            'data_nascimento': data_nascimento,
            'is_admin': is_admin,
        }

        # Insere no banco
        try:
            new_id = db.insert_usuario(usuario)
            ColorMsg.print_success(f'\n✓ Usuário cadastrado com sucesso! ID: {new_id}')
        except DatabaseError as e:
            ColorMsg.print_error(f'\n✗ Erro ao inserir usuário: {e}')
        except Exception as e:
            ColorMsg.print_error(f'\n✗ Erro inesperado ao inserir usuário: {e}')

    except KeyboardInterrupt:
        ColorMsg.print_warning('\n\n✗ Operação cancelada pelo usuário.')
    except Exception as e:
        ColorMsg.print_error(f'\n✗ Erro ao cadastrar usuário: {e}')


def listar_usuarios():
    """Lista todos os usuários cadastrados."""
    try:
        if db is None:
            ColorMsg.print_error('✗ Adaptador Oracle não disponível.')
            return

        usuarios = db.list_usuarios()

        if not usuarios:
            ColorMsg.print_warning('\n⚠ Nenhum usuário cadastrado.')
            return

        ColorMsg.print_title('\n' + '=' * 60)
        ColorMsg.print_title(f'LISTA DE USUÁRIOS ({len(usuarios)} cadastrado(s))')
        ColorMsg.print_title('=' * 60)

        for usuario in usuarios:
            ColorMsg.print_info(format_usuario_display(usuario))

    except Exception as e:
        ColorMsg.print_error(f'\n✗ Erro ao listar usuários: {e}')


def buscar_usuario_por_id():
    """Busca e exibe um usuário específico por ID."""
    try:
        if db is None:
            ColorMsg.print_error('✗ Adaptador Oracle não disponível.')
            return

        id_usuario, success = _input_with_validation(
            ColorMsg.INPUT + '\nID do usuário: ' + ColorMsg.RESET,
            validate_id,
            field_name='ID',
        )

        if not success or not id_usuario:
            return

        usuario = db.get_usuario_por_id(id_usuario)

        if not usuario:
            ColorMsg.print_error(f'\n✗ Usuário com ID {id_usuario} não encontrado.')
            return

        ColorMsg.print_title('\n' + '=' * 60)
        ColorMsg.print_title('DADOS DO USUÁRIO')
        ColorMsg.print_title('=' * 60)
        ColorMsg.print_info(f'ID:              {usuario.get("id_usuario")}')
        ColorMsg.print_info(f'Nome:            {usuario.get("nome_completo")}')
        ColorMsg.print_info(f'Email:           {usuario.get("email")}')
        ColorMsg.print_info(f'Empresa ID:      {usuario.get("id_empresa") or "N/A"}')
        ColorMsg.print_info(f'Nível:           {usuario.get("nivel_carreira")}')
        ColorMsg.print_info(f'Ocupação:        {usuario.get("ocupacao")}')
        ColorMsg.print_info(f'Gênero:          {usuario.get("genero")}')
        ColorMsg.print_info(
            f'Nascimento:      {usuario.get("data_nascimento") or "N/A"}'
        )
        ColorMsg.print_info(f'Cadastrado em:   {usuario.get("data_cadastro")}')
        ColorMsg.print_info(
            f'Administrador:   {"Sim" if usuario.get("is_admin") == 1 else "Não"}'
        )
        ColorMsg.print_title('=' * 60)

    except Exception as e:
        ColorMsg.print_error(f'\n✗ Erro ao buscar usuário: {e}')


def atualizar_usuario():
    """Atualiza dados de um usuário existente."""
    try:
        if db is None:
            ColorMsg.print_error('✗ Adaptador Oracle não disponível.')
            return

        listar_usuarios()

        id_usuario, success = _input_with_validation(
            '\nID do usuário a atualizar: ', validate_id, field_name='ID'
        )

        if not success or not id_usuario:
            return

        usuario = db.get_usuario_por_id(id_usuario)
        if not usuario:
            ColorMsg.print_error('\n✗ Usuário não encontrado.')
            return

        ColorMsg.print_info(f'\nAtualizando: {usuario.get("nome_completo")}')

        while True:
            ColorMsg.print_menu('\n' + '-' * 60)
            ColorMsg.print_menu('MENU DE ATUALIZAÇÃO')
            ColorMsg.print_menu('-' * 60)
            ColorMsg.print_menu('1 - ID da empresa')
            ColorMsg.print_menu('2 - Nome completo')
            ColorMsg.print_menu('3 - Email')
            ColorMsg.print_menu('4 - Senha')
            ColorMsg.print_menu('5 - Nível de carreira')
            ColorMsg.print_menu('6 - Ocupação')
            ColorMsg.print_menu('7 - Gênero')
            ColorMsg.print_menu('8 - Data de nascimento')
            ColorMsg.print_menu('9 - Flag admin')
            ColorMsg.print_menu('0 - Salvar e voltar')
            ColorMsg.print_menu('-' * 60)

            escolha = ColorMsg.input_prompt('Escolha: ').strip()

            if escolha == '1':
                novo_id, _ = validate_id(
                    ColorMsg.input_prompt(
                        'Novo ID da empresa (vazio para remover): '
                    ).strip()
                )
                usuario['id_empresa'] = novo_id
                ColorMsg.print_success('✓ ID da empresa atualizado.')

            elif escolha == '2':
                novo, success = _input_with_validation(
                    ColorMsg.INPUT + 'Novo nome completo: ' + ColorMsg.RESET,
                    validate_string_field,
                    field_name='Nome',
                    max_length=MAX_NOME_COMPLETO,
                    required=True,
                )
                if success:
                    usuario['nome_completo'] = novo
                    ColorMsg.print_success('✓ Nome atualizado.')

            elif escolha == '3':
                novo, success = _input_with_validation(
                    ColorMsg.INPUT + 'Novo email: ' + ColorMsg.RESET, validate_email
                )
                if success:
                    if db.email_existe(novo, exclude_id=id_usuario):
                        ColorMsg.print_error('✗ Email já cadastrado.')
                    else:
                        usuario['email'] = novo
                        ColorMsg.print_success('✓ Email atualizado.')

            elif escolha == '4':
                novo = ColorMsg.input_prompt('Nova senha: ').strip()
                if novo:
                    usuario['senha_hash'] = hashlib.sha256(
                        novo.encode('utf-8')
                    ).hexdigest()
                    ColorMsg.print_success('✓ Senha atualizada.')
                else:
                    ColorMsg.print_warning('⚠ Senha não alterada.')

            elif escolha == '5':
                novo, _ = _input_with_validation(
                    ColorMsg.INPUT + 'Novo nível de carreira: ' + ColorMsg.RESET,
                    validate_string_field,
                    field_name='Nível',
                    max_length=MAX_NIVEL_CARREIRA,
                    required=False,
                    default='Não especificado',
                )
                usuario['nivel_carreira'] = novo
                ColorMsg.print_success('✓ Nível atualizado.')

            elif escolha == '6':
                novo, _ = _input_with_validation(
                    ColorMsg.INPUT + 'Nova ocupação: ' + ColorMsg.RESET,
                    validate_string_field,
                    field_name='Ocupação',
                    max_length=MAX_OCUPACAO,
                    required=False,
                    default='Não especificado',
                )
                usuario['ocupacao'] = novo
                ColorMsg.print_success('✓ Ocupação atualizada.')

            elif escolha == '7':
                novo, _ = _input_with_validation(
                    ColorMsg.INPUT + 'Novo gênero: ' + ColorMsg.RESET,
                    validate_string_field,
                    field_name='Gênero',
                    max_length=MAX_GENERO,
                    required=False,
                    default='Não especificado',
                )
                usuario['genero'] = novo
                ColorMsg.print_success('✓ Gênero atualizado.')

            elif escolha == '8':
                # Atualizar data de nascimento (DD/MM/YYYY)
                while True:
                    novo_input = input_date_mask(
                        ColorMsg.INPUT
                        + 'Nova data de nascimento (DD/MM/YYYY, vazio para manter): '
                        + ColorMsg.RESET
                    ).strip()
                    # Se vazio, mantém o valor atual
                    if novo_input == '':
                        ColorMsg.print_success('✓ Data mantida.')
                        break

                    novo_val, novo_err = validate_date(novo_input, required=True)
                    if novo_err:
                        ColorMsg.print_error(f'✗ {novo_err}')
                        continue

                    if novo_val is not None:
                        usuario['data_nascimento'] = novo_val
                        ColorMsg.print_success('✓ Data atualizada.')
                    else:
                        ColorMsg.print_error('✗ Data de nascimento é obrigatória.')
                        continue
                    break

            elif escolha == '9':
                novo_admin = ColorMsg.input_prompt('É administrador? (s/n): ').strip()
                usuario['is_admin'] = 1 if validate_boolean_input(novo_admin) else 0
                ColorMsg.print_success('✓ Flag admin atualizada.')

            elif escolha == '0':
                try:
                    db.update_usuario(id_usuario, usuario)
                    ColorMsg.print_success('\n✓ Alterações salvas com sucesso!')
                    break
                except DatabaseError as e:
                    ColorMsg.print_error(f'\n✗ Erro ao salvar: {e}')
                    break
                except Exception as e:
                    ColorMsg.print_error(f'\n✗ Erro inesperado ao salvar: {e}')
                    break
            else:
                ColorMsg.print_error('✗ Opção inválida.')

    except KeyboardInterrupt:
        ColorMsg.print_warning('\n\n✗ Operação cancelada.')
    except Exception as e:
        ColorMsg.print_error(f'\n✗ Erro ao atualizar usuário: {e}')


def deletar_usuario():
    """Remove um usuário do sistema."""
    try:
        if db is None:
            ColorMsg.print_error('✗ Adaptador Oracle não disponível.')
            return

        listar_usuarios()

        id_usuario, success = _input_with_validation(
            ColorMsg.INPUT + '\nID do usuário a remover: ' + ColorMsg.RESET,
            validate_id,
            field_name='ID',
        )

        if not success or not id_usuario:
            return

        usuario = db.get_usuario_por_id(id_usuario)
        if not usuario:
            ColorMsg.print_error('\n✗ Usuário não encontrado.')
            return

        nome = usuario.get('nome_completo')
        confirm = ColorMsg.input_prompt(
            f"\n⚠ Confirma exclusão de '{nome}'? (s/n): "
        ).strip()

        if validate_boolean_input(confirm):
            try:
                db.delete_usuario(id_usuario)
                ColorMsg.print_success(f'\n✓ Usuário "{nome}" removido com sucesso!')
            except DatabaseError as e:
                ColorMsg.print_error(f'\n✗ Erro ao remover: {e}')
            except Exception as e:
                ColorMsg.print_error(f'\n✗ Erro inesperado ao remover: {e}')
        else:
            ColorMsg.print_warning('\n✗ Exclusão cancelada.')

    except KeyboardInterrupt:
        ColorMsg.print_warning('\n\n✗ Operação cancelada.')
    except Exception as e:
        ColorMsg.print_error(f'\n✗ Erro ao deletar usuário: {e}')
