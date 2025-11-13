from storage import carregar_dados, salvar_dados

ARQUIVO_EMPRESAS = 'empresas.json'


def criar_empresa():
    try:
        empresas = carregar_dados(ARQUIVO_EMPRESAS)
        nome = input("Digite o nome da empresa: ").strip()
        if not nome:
            print("Nome não pode ser vazio.")
            return
        cnpj = input("Digite o CNPJ: ").strip()
        if not cnpj or not cnpj.isdigit() or len(cnpj) != 14:
            print("CNPJ deve conter 14 dígitos numéricos.")
            return
        # Verifica se CNPJ já existe
        if any(e['cnpj'] == cnpj for e in empresas):
            print("CNPJ já cadastrado.")
            return
        empresa = {
            'id': len(empresas) + 1,
            'nome': nome,
            'cnpj': cnpj
        }
        empresas.append(empresa)
        salvar_dados(ARQUIVO_EMPRESAS, empresas)
        print("Empresa cadastrada com sucesso!")
    except Exception as e:
        print("Erro ao cadastrar empresa:", e)


def listar_empresas():
    try:
        empresas = carregar_dados(ARQUIVO_EMPRESAS)
        if not empresas:
            print("Nenhuma empresa cadastrada.")
            return
        print("\nLista de Empresas:")
        for empresa in empresas:
            print(f"ID: {empresa['id']} | Nome: {empresa['nome']} | CNPJ: {empresa['cnpj']}")
    except Exception as e:
        print("Erro ao listar empresas:", e)


def atualizar_empresa():
    pass


def deletar_empresa():
    pass


def buscar_empresa_por_id():
    pass


def buscar_empresa_por_nome():
    pass


def exportar_empresas_json():
    pass
