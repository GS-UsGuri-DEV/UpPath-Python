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
    try:
        empresas = carregar_dados(ARQUIVO_EMPRESAS)
        if not empresas:
            print("Nenhuma empresa cadastrada.")
            return
        listar_empresas()
        id_str = input("\nDigite o ID da empresa a atualizar: ").strip()
        if not id_str.isdigit():
            print("ID inválido.")
            return
        id_empresa = int(id_str)
        empresa = next((e for e in empresas if e['id'] == id_empresa), None)
        if not empresa:
            print("Empresa não encontrada.")
            return
        print(f"\nEmpresa atual: {empresa['nome']} | CNPJ: {empresa['cnpj']}")
        nome = input("Novo nome (Enter para manter): ").strip()
        if nome:
            empresa['nome'] = nome
        cnpj = input("Novo CNPJ (Enter para manter): ").strip()
        if cnpj:
            if not cnpj.isdigit() or len(cnpj) != 14:
                print("CNPJ deve conter 14 dígitos numéricos.")
                return
            if any(e['cnpj'] == cnpj and e['id'] != id_empresa for e in empresas):
                print("CNPJ já cadastrado.")
                return
            empresa['cnpj'] = cnpj
        salvar_dados(ARQUIVO_EMPRESAS, empresas)
        print("Empresa atualizada com sucesso!")
    except Exception as e:
        print("Erro ao atualizar empresa:", e)


def deletar_empresa():
    try:
        empresas = carregar_dados(ARQUIVO_EMPRESAS)
        if not empresas:
            print("Nenhuma empresa cadastrada.")
            return
        listar_empresas()
        id_str = input("\nDigite o ID da empresa a remover: ").strip()
        if not id_str.isdigit():
            print("ID inválido.")
            return
        id_empresa = int(id_str)
        empresa = next((e for e in empresas if e['id'] == id_empresa), None)
        if not empresa:
            print("Empresa não encontrada.")
            return
        confirmacao = input(f"Confirma a exclusão de '{empresa['nome']}'? (s/n): ").strip().lower()
        if confirmacao == 's':
            empresas.remove(empresa)
            # Reindexa os IDs para manter sequencialidade
            for idx, e in enumerate(empresas, start=1):
                e['id'] = idx
            salvar_dados(ARQUIVO_EMPRESAS, empresas)
            print("Empresa removida com sucesso!")
        else:
            print("Exclusão cancelada.")
    except Exception as e:
        print("Erro ao deletar empresa:", e)


def buscar_empresa_por_id():
    pass


def buscar_empresa_por_nome():
    pass


def exportar_empresas_json():
    pass
