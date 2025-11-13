# crud_usuarios.py
# CRUD para usuários

from storage import carregar_dados, salvar_dados

ARQUIVO_USUARIOS = 'usuarios.json'


def criar_usuario():
    try:
        usuarios = carregar_dados(ARQUIVO_USUARIOS)
        nome = input('Digite o nome do usuário: ').strip()
        if not nome:
            print('Nome não pode ser vazio.')
            return
        email = input('Digite o email: ').strip()
        if not email or '@' not in email:
            print('Email inválido.')
            return
        # Verifica se email já existe
        if any(u.get('email') == email for u in usuarios):
            print('Email já cadastrado.')
            return
        telefone = input('Digite o telefone: ').strip()
        if not telefone:
            print('Telefone não pode ser vazio.')
            return
        usuario = {
            'id': len(usuarios) + 1,
            'nome': nome,
            'email': email,
            'telefone': telefone,
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
                f'ID: {usuario["id"]} | Nome: {usuario["nome"]} | Email: {usuario["email"]} | Telefone: {usuario["telefone"]}'
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
