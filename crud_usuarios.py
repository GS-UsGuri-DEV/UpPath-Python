import hashlib
import re
from datetime import datetime
import storage_oracle as db



def criar_usuario():
    try:
        if db is None:
            print(
                'Adaptador Oracle não disponível. Instale/configure o driver e o módulo storage_oracle.'
            )
            return

        db.init_table()

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
        if not is_valid_email(email):
            print('Email inválido.')
            return

        if db.email_existe(email):
            print('Email já cadastrado.')
            return

        senha = input('Digite a senha (será armazenada como hash): ').strip()
        if not senha:
            print('Senha não pode ser vazia.')
            return
        senha_hash = hashlib.sha256(senha.encode('utf-8')).hexdigest()

        nivel_carreira = (
            input('Nível de carreira (ex: Júnior/Pleno/Sênior): ').strip() or ''
        )
        ocupacao = input('Ocupação (cargo): ').strip() or ''
        genero = input('Gênero: ').strip() or ''

        data_nascimento = input('Data de nascimento (YYYY-MM-DD): ').strip()
        if data_nascimento:
            try:
                dn_val = datetime.strptime(data_nascimento, '%Y-%m-%d').date()
            except Exception:
                print('Data de nascimento inválida. Use YYYY-MM-DD.')
                return
        else:
            dn_val = None

        is_admin_input = input('É administrador? (s/n) [n]: ').strip().lower() or 'n'
        is_admin = 1 if is_admin_input == 's' else 0

        usuario = {
            'id_empresa': id_empresa,
            'nome_completo': nome_completo,
            'email': email,
            'senha_hash': senha_hash,
            'nivel_carreira': nivel_carreira,
            'ocupacao': ocupacao,
            'genero': genero,
            'data_nascimento': dn_val,
            'is_admin': is_admin,
        }

        try:
            new_id = db.insert_usuario(usuario)
            print(f'Usuário cadastrado com sucesso! (Oracle) id={new_id}')
        except Exception as e:
            print('Erro ao inserir usuário no Oracle:', e)
    except Exception as e:
        print('Erro ao cadastrar usuário:', e)


def listar_usuarios():
    try:
        if db is None:
            print('Adaptador Oracle não disponível.')
            return
        db.init_table()
        usuarios = db.list_usuarios()

        if not usuarios:
            print('Nenhum usuário cadastrado.')
            return
        print('\nLista de Usuários:')
        for usuario in usuarios:
            print(
                f'ID: {usuario.get("id_usuario")} | Nome: {usuario.get("nome_completo")} | Email: {usuario.get("email")} | Empresa: {usuario.get("id_empresa")} | Nivel: {usuario.get("nivel_carreira")} | Ocupacao: {usuario.get("ocupacao")} | Genero: {usuario.get("genero")} | Nasc: {usuario.get("data_nascimento")} | Cadastrado: {usuario.get("data_cadastro")} | Admin: {usuario.get("is_admin")}'
            )
    except Exception as e:
        print('Erro ao listar usuários:', e)


def is_valid_email(email: str) -> bool:
    """Validação simples de e-mail usando regex."""
    if not email:
        return False
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None


def atualizar_usuario():
    try:
        if db is None:
            print('Adaptador Oracle não disponível.')
            return
        db.init_table()
        listar_usuarios()
        id_str = input('\nDigite o ID do usuário a atualizar: ').strip()
        if not id_str.isdigit():
            print('ID inválido.')
            return
        id_usuario = int(id_str)
        usuario = db.get_usuario_por_id(id_usuario)

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
                if not is_valid_email(novo):
                    print('Email inválido.')
                else:
                    # checa duplicidade
                    if db.email_existe(novo, exclude_id=id_usuario):
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
                # aplica alterações no banco via API
                try:
                    db.update_usuario(id_usuario, usuario)
                    print('Alterações salvas (Oracle).')
                    break
                except Exception as e:
                    print('Erro ao atualizar usuário no Oracle:', e)
                    break
            else:
                print('Opção inválida.')
    except Exception as e:
        print('Erro ao atualizar usuário:', e)


def deletar_usuario():
    try:
        if db is None:
            print('Adaptador Oracle não disponível.')
            return
        listar_usuarios()
        id_str = input('\nDigite o ID do usuário a remover: ').strip()
        if not id_str.isdigit():
            print('ID inválido.')
            return
        id_usuario = int(id_str)
        # busca nome para confirmação
        u = db.get_usuario_por_id(id_usuario)
        if not u:
            print('Usuário não encontrado.')
            return
        nome = u.get('nome_completo')

        confirm = input(f"Confirma a exclusão de '{nome}'? (s/n): ").strip().lower()
        if confirm == 's':
            try:
                db.delete_usuario(id_usuario)
                print('Usuário removido com sucesso! (Oracle)')
            except Exception as e:
                print('Erro ao remover usuário no Oracle:', e)
        else:
            print('Exclusão cancelada.')
    except Exception as e:
        print('Erro ao deletar usuário:', e)
