"""
Interface de usuário para operações CRUD de usuários.
"""

import hashlib

from services import storage_oracle as db
from utils.db_utils import format_usuario_display
from utils.validators import (
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
    user_input = input(prompt).strip()
    value, error = validator_func(user_input, **kwargs)

    if error:
        print(f'✗ {error}')
        return None, False

    return value, True


def criar_usuario():
    """Cria um novo usuário com validações completas."""
    try:
        if db is None:
            print('✗ Adaptador Oracle não disponível.')
            return

        print('\n' + '=' * 60)
        print('CADASTRO DE NOVO USUÁRIO')
        print('=' * 60)

        # ID da empresa (opcional)
        id_empresa_str = input('ID da empresa (opcional, Enter para pular): ').strip()
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
            print('✗ Email já cadastrado.')
            return

        # Senha
        senha = input('Senha: ').strip()
        if not senha:
            print('✗ Senha não pode ser vazia.')
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
                'Data de nascimento (DD/MM/YYYY, opcional): '
            ).strip()
            dn_val, dn_err = validate_date(dn_input, required=False)
            if dn_err:
                print(f'✗ {dn_err}')
                continue
            data_nascimento = dn_val
            break

        # Administrador
        is_admin_input = input('É administrador? (s/n) [n]: ').strip()
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
            print(f'\n✓ Usuário cadastrado com sucesso! ID: {new_id}')
        except Exception as e:
            print(f'\n✗ Erro ao inserir usuário: {e}')

    except KeyboardInterrupt:
        print('\n\n✗ Operação cancelada pelo usuário.')
    except Exception as e:
        print(f'\n✗ Erro ao cadastrar usuário: {e}')


def listar_usuarios():
    """Lista todos os usuários cadastrados."""
    try:
        if db is None:
            print('✗ Adaptador Oracle não disponível.')
            return

        usuarios = db.list_usuarios()

        if not usuarios:
            print('\n⚠ Nenhum usuário cadastrado.')
            return

        print('\n' + '=' * 60)
        print(f'LISTA DE USUÁRIOS ({len(usuarios)} cadastrado(s))')
        print('=' * 60)

        for usuario in usuarios:
            print(format_usuario_display(usuario))

    except Exception as e:
        print(f'\n✗ Erro ao listar usuários: {e}')


def buscar_usuario_por_id():
    """Busca e exibe um usuário específico por ID."""
    try:
        if db is None:
            print('✗ Adaptador Oracle não disponível.')
            return

        id_usuario, success = _input_with_validation(
            '\nID do usuário: ', validate_id, field_name='ID'
        )

        if not success or not id_usuario:
            return

        usuario = db.get_usuario_por_id(id_usuario)

        if not usuario:
            print(f'\n✗ Usuário com ID {id_usuario} não encontrado.')
            return

        print('\n' + '=' * 60)
        print('DADOS DO USUÁRIO')
        print('=' * 60)
        print(f'ID:              {usuario.get("id_usuario")}')
        print(f'Nome:            {usuario.get("nome_completo")}')
        print(f'Email:           {usuario.get("email")}')
        print(f'Empresa ID:      {usuario.get("id_empresa") or "N/A"}')
        print(f'Nível:           {usuario.get("nivel_carreira")}')
        print(f'Ocupação:        {usuario.get("ocupacao")}')
        print(f'Gênero:          {usuario.get("genero")}')
        print(f'Nascimento:      {usuario.get("data_nascimento") or "N/A"}')
        print(f'Cadastrado em:   {usuario.get("data_cadastro")}')
        print(f'Administrador:   {"Sim" if usuario.get("is_admin") == 1 else "Não"}')
        print('=' * 60)

    except Exception as e:
        print(f'\n✗ Erro ao buscar usuário: {e}')


def atualizar_usuario():
    """Atualiza dados de um usuário existente."""
    try:
        if db is None:
            print('✗ Adaptador Oracle não disponível.')
            return

        listar_usuarios()

        id_usuario, success = _input_with_validation(
            '\nID do usuário a atualizar: ', validate_id, field_name='ID'
        )

        if not success or not id_usuario:
            return

        usuario = db.get_usuario_por_id(id_usuario)
        if not usuario:
            print('\n✗ Usuário não encontrado.')
            return

        print(f'\nAtualizando: {usuario.get("nome_completo")}')

        while True:
            print('\n' + '-' * 60)
            print('MENU DE ATUALIZAÇÃO')
            print('-' * 60)
            print('1 - ID da empresa')
            print('2 - Nome completo')
            print('3 - Email')
            print('4 - Senha')
            print('5 - Nível de carreira')
            print('6 - Ocupação')
            print('7 - Gênero')
            print('8 - Data de nascimento')
            print('9 - Flag admin')
            print('0 - Salvar e voltar')
            print('-' * 60)

            escolha = input('Escolha: ').strip()

            if escolha == '1':
                novo_id, _ = validate_id(
                    input('Novo ID da empresa (vazio para remover): ').strip()
                )
                usuario['id_empresa'] = novo_id
                print('✓ ID da empresa atualizado.')

            elif escolha == '2':
                novo, success = _input_with_validation(
                    'Novo nome completo: ',
                    validate_string_field,
                    field_name='Nome',
                    max_length=MAX_NOME_COMPLETO,
                    required=True,
                )
                if success:
                    usuario['nome_completo'] = novo
                    print('✓ Nome atualizado.')

            elif escolha == '3':
                novo, success = _input_with_validation('Novo email: ', validate_email)
                if success:
                    if db.email_existe(novo, exclude_id=id_usuario):
                        print('✗ Email já cadastrado.')
                    else:
                        usuario['email'] = novo
                        print('✓ Email atualizado.')

            elif escolha == '4':
                novo = input('Nova senha: ').strip()
                if novo:
                    usuario['senha_hash'] = hashlib.sha256(
                        novo.encode('utf-8')
                    ).hexdigest()
                    print('✓ Senha atualizada.')
                else:
                    print('⚠ Senha não alterada.')

            elif escolha == '5':
                novo, _ = _input_with_validation(
                    'Novo nível de carreira: ',
                    validate_string_field,
                    field_name='Nível',
                    max_length=MAX_NIVEL_CARREIRA,
                    required=False,
                    default='Não especificado',
                )
                usuario['nivel_carreira'] = novo
                print('✓ Nível atualizado.')

            elif escolha == '6':
                novo, _ = _input_with_validation(
                    'Nova ocupação: ',
                    validate_string_field,
                    field_name='Ocupação',
                    max_length=MAX_OCUPACAO,
                    required=False,
                    default='Não especificado',
                )
                usuario['ocupacao'] = novo
                print('✓ Ocupação atualizada.')

            elif escolha == '7':
                novo, _ = _input_with_validation(
                    'Novo gênero: ',
                    validate_string_field,
                    field_name='Gênero',
                    max_length=MAX_GENERO,
                    required=False,
                    default='Não especificado',
                )
                usuario['genero'] = novo
                print('✓ Gênero atualizado.')

            elif escolha == '8':
                # Atualizar data de nascimento (DD/MM/YYYY)
                while True:
                    novo_input = input_date_mask(
                        'Nova data de nascimento (DD/MM/YYYY, vazio para manter): '
                    ).strip()
                    # Se vazio, mantém o valor atual 
                    if novo_input == '':
                        print('✓ Data mantida.')
                        break

                    novo_val, novo_err = validate_date(novo_input, required=True)
                    if novo_err:
                        print(f'✗ {novo_err}')
                        continue
                    
                    if novo_val is not None:
                        usuario['data_nascimento'] = novo_val
                        print('✓ Data atualizada.')
                    else:
                        print('✗ Data de nascimento é obrigatória.')
                        continue
                    break

            elif escolha == '9':
                novo_admin = input('É administrador? (s/n): ').strip()
                usuario['is_admin'] = 1 if validate_boolean_input(novo_admin) else 0
                print('✓ Flag admin atualizada.')

            elif escolha == '0':
                try:
                    db.update_usuario(id_usuario, usuario)
                    print('\n✓ Alterações salvas com sucesso!')
                    break
                except Exception as e:
                    print(f'\n✗ Erro ao salvar: {e}')
                    break
            else:
                print('✗ Opção inválida.')

    except KeyboardInterrupt:
        print('\n\n✗ Operação cancelada.')
    except Exception as e:
        print(f'\n✗ Erro ao atualizar usuário: {e}')


def deletar_usuario():
    """Remove um usuário do sistema."""
    try:
        if db is None:
            print('✗ Adaptador Oracle não disponível.')
            return

        listar_usuarios()

        id_usuario, success = _input_with_validation(
            '\nID do usuário a remover: ', validate_id, field_name='ID'
        )

        if not success or not id_usuario:
            return

        usuario = db.get_usuario_por_id(id_usuario)
        if not usuario:
            print('\n✗ Usuário não encontrado.')
            return

        nome = usuario.get('nome_completo')
        confirm = input(f"\n⚠ Confirma exclusão de '{nome}'? (s/n): ").strip()

        if validate_boolean_input(confirm):
            try:
                db.delete_usuario(id_usuario)
                print(f'\n✓ Usuário "{nome}" removido com sucesso!')
            except Exception as e:
                print(f'\n✗ Erro ao remover: {e}')
        else:
            print('\n✗ Exclusão cancelada.')

    except KeyboardInterrupt:
        print('\n\n✗ Operação cancelada.')
    except Exception as e:
        print(f'\n✗ Erro ao deletar usuário: {e}')
