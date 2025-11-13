# storage.py
# Funções para carregar e salvar dados em JSON
import json
import os


def carregar_dados(arquivo):
    try:
        if not os.path.exists(arquivo):
            return []
        with open(arquivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f'Erro ao carregar dados: {e}')
        return []


def salvar_dados(arquivo, dados):
    try:
        with open(arquivo, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f'Erro ao salvar dados: {e}')
