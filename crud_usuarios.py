import hashlib
from datetime import date, datetime

from storage import carregar_dados, salvar_dados

ARQUIVO_USUARIOS = 'usuarios.json'


def criar_usuario():
    try:
        usuarios = carregar_dados(ARQUIVO_USUARIOS)

        id_empresa = input('ID da empresa (opcional, Enter para nenhum): ').strip()
        if id_empresa and not id_empresa.isdigit():
            print('ID da empresa inválido.')
            return
        id_empresa = int(id_empresa) if id_empresa else None

        nome_completo = input('Digite o nome completo: ').strip()
        if not nome_completo:
            print('Nome completo não pode ser vazio.')
            return

        email = input('Digite o email: ').strip()
        if not email or '@' not in email:
            print('Email inválido.')
            return
        if any(u.get('email') == email for u in usuarios):
            print('Email já cadastrado.')
            return

        senha = input('Digite a senha (será armazenada como hash): ').strip()
        if not senha:
            print('Senha não pode ser vazia.')
            return
        senha_hash = hashlib.sha256(senha.encode('utf-8')).hexdigest()

        nivel_carreira = (
            input('Nível de carreira (ex: Júnior/Pleno/Sênior) [opcional]: ').strip()
            or None
        )
        ocupacao = input('Ocupação (cargo) [opcional]: ').strip() or None
        genero = input('Gênero [opcional]: ').strip() or None

        data_nascimento = input('Data de nascimento (YYYY-MM-DD) [opcional]: ').strip()
        if data_nascimento:
            try:
                # valida formato
                datetime.strptime(data_nascimento, '%Y-%m-%d')
            except Exception:
                print('Data de nascimento inválida. Use YYYY-MM-DD.')
                return
        else:
            data_nascimento = None

        data_cadastro = date.today().isoformat()

        is_admin_input = input('É administrador? (s/n) [n]: ').strip().lower() or 'n'
        is_admin = 1 if is_admin_input == 's' else 0

        usuario = {
            'id': len(usuarios) + 1,
            'id_empresa': id_empresa,
            'nome_completo': nome_completo,
            'email': email,
            'senha_hash': senha_hash,
            'nivel_carreira': nivel_carreira,
            'ocupacao': ocupacao,
            'genero': genero,
            'data_nascimento': data_nascimento,
            'data_cadastro': data_cadastro,
            'is_admin': is_admin,
        }

        usuarios.append(usuario)
        salvar_dados(ARQUIVO_USUARIOS, usuarios)
        print('Usuário cadastrado com sucesso!')
    except Exception as e:
        print('Erro ao cadastrar usuário:', e)


def listar_usuarios():
    try:
        usuarios = carregar_dados(ARQUIVO_USUARIOS)
        if not usuarios:
            print('Nenhum usuário cadastrado.')
            return
        print('\nLista de Usuários:')
        for usuario in usuarios:
            print(
                f'ID: {usuario.get("id")} | Nome: {usuario.get("nome_completo")} | Email: {usuario.get("email")} | Empresa: {usuario.get("id_empresa")} | Nivel: {usuario.get("nivel_carreira")} | Ocupacao: {usuario.get("ocupacao")} | Genero: {usuario.get("genero")} | Nasc: {usuario.get("data_nascimento")} | Cadastrado: {usuario.get("data_cadastro")} | Admin: {usuario.get("is_admin")}'
            )
    except Exception as e:
        print('Erro ao listar usuários:', e)


def atualizar_usuario():
    try:
        usuarios = carregar_dados(ARQUIVO_USUARIOS)
        if not usuarios:
            print('Nenhum usuário cadastrado.')
            return
        listar_usuarios()
        id_str = input('\nDigite o ID do usuário a atualizar: ').strip()
        if not id_str.isdigit():
            print('ID inválido.')
            return
        id_usuario = int(id_str)
        usuario = next((u for u in usuarios if u['id'] == id_usuario), None)
        if not usuario:
            print('Usuário não encontrado.')
            return

        while True:
            print('\n--- Atualizar Usuário ---')
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
            escolha = input('Escolha opção: ').strip()

            if escolha == '1':
                novo = input(
                    'Novo ID da empresa (vazio para remover vínculo): '
                ).strip()
                if novo == '':
                    usuario['id_empresa'] = None
                    print('Vínculo com empresa removido.')
                elif not novo.isdigit():
                    print('ID inválido.')
                else:
                    usuario['id_empresa'] = int(novo)
                    print('ID da empresa atualizado.')
            elif escolha == '2':
                novo = input('Novo nome completo: ').strip()
                if novo:
                    usuario['nome_completo'] = novo
                    print('Nome atualizado.')
                else:
                    print('Nenhuma alteração.')
            elif escolha == '3':
                novo = input('Novo email: ').strip()
                if not novo or '@' not in novo:
                    print('Email inválido.')
                elif any(
                    u.get('email') == novo and u['id'] != id_usuario for u in usuarios
                ):
                    print('Email já cadastrado.')
                else:
                    usuario['email'] = novo
                    print('Email atualizado.')
            elif escolha == '4':
                novo = input('Nova senha: ').strip()
                if novo:
                    usuario['senha_hash'] = hashlib.sha256(
                        novo.encode('utf-8')
                    ).hexdigest()
                    print('Senha atualizada.')
                else:
                    print('Nenhuma alteração na senha.')
            elif escolha == '5':
                novo = input('Novo nível de carreira: ').strip()
                usuario['nivel_carreira'] = novo or usuario.get('nivel_carreira')
                print('Nível de carreira atualizado.')
            elif escolha == '6':
                novo = input('Nova ocupação: ').strip()
                usuario['ocupacao'] = novo or usuario.get('ocupacao')
                print('Ocupação atualizada.')
            elif escolha == '7':
                novo = input('Novo gênero: ').strip()
                usuario['genero'] = novo or usuario.get('genero')
                print('Gênero atualizado.')
            elif escolha == '8':
                novo = input('Nova data de nascimento (YYYY-MM-DD): ').strip()
                if novo:
                    try:
                        datetime.strptime(novo, '%Y-%m-%d')
                        usuario['data_nascimento'] = novo
                        print('Data de nascimento atualizada.')
                    except Exception:
                        print('Formato inválido. Use YYYY-MM-DD.')
                else:
                    print('Nenhuma alteração.')
            elif escolha == '9':
                novo = input('É administrador? (s/n): ').strip().lower()
                if novo in ('s', 'n'):
                    usuario['is_admin'] = 1 if novo == 's' else 0
                    print('Flag admin atualizada.')
                else:
                    print('Entrada inválida.')
            elif escolha == '0':
                salvar_dados(ARQUIVO_USUARIOS, usuarios)
                print('Alterações salvas.')
                break
            else:
                print('Opção inválida.')
    except Exception as e:
        print('Erro ao atualizar usuário:', e)


def deletar_usuario():
    pass


def buscar_usuario_por_id():
    pass


def buscar_usuario_por_nome():
    pass


def exportar_usuarios_json():
    pass
