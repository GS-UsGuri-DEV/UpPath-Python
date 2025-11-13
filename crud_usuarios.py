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
    pass


def deletar_usuario():
    pass


def buscar_usuario_por_id():
    pass


def buscar_usuario_por_nome():
    pass


def exportar_usuarios_json():
    pass
