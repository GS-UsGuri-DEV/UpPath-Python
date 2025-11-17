"""
Camada para sincronizar usuários com banco Oracle e executar consultas.
"""

import logging
import os
from typing import Dict

try:
    import oracledb
except ImportError:
    oracledb = None

logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s'
)


def _connect(conn_info: Dict = None):
    """Cria e retorna uma conexão direta com o banco Oracle.

    Nota: o suporte a pool foi removido para simplificar o uso em ambientes
    onde o pool não é necessário. Quem usar esta função deve fechar a
    conexão com `conn.close()` quando terminar.
    """
    if oracledb is None:
        raise ModuleNotFoundError('oracledb não encontrado')

    if conn_info is None:
        try:
            from src.config import get_db_config

            cfg = get_db_config()
        except Exception:
            cfg = None

        if cfg is None:
            user = os.getenv('ORACLE_USER')
            password = os.getenv('ORACLE_PASSWORD')
            dsn = os.getenv('ORACLE_DSN')
        else:
            user = cfg.get('user')
            password = cfg.get('password')
            dsn = cfg.get('dsn')
    else:
        user = conn_info.get('user')
        password = conn_info.get('password')
        dsn = conn_info.get('dsn')

    if not (user and password and dsn):
        raise ValueError('Informação de conexão Oracle incompleta')

    return oracledb.connect(user=user, password=password, dsn=dsn)


def init_table(conn_info: Dict = None):
    """Cria tabelas e sequence se não existirem. Ajusta sequence START baseado em dados existentes."""
    conn = _connect(conn_info)
    cur = conn.cursor()
    try:
        # Criar tabela empresas
        cur.execute(
            """
            BEGIN
                EXECUTE IMMEDIATE '
                CREATE TABLE empresas (
                    id_empresa NUMBER(6) NOT NULL,
                    nome_empresa VARCHAR2(60) NOT NULL,
                    cnpj VARCHAR2(18) NOT NULL,
                    email_contato VARCHAR2(60) NOT NULL,
                    data_cadastro TIMESTAMP WITH TIME ZONE DEFAULT SYSTIMESTAMP NOT NULL,
                    CONSTRAINT empresas_PK PRIMARY KEY (id_empresa),
                    CONSTRAINT empresas_cnpj_uk UNIQUE (cnpj),
                    CONSTRAINT empresas_email_uk UNIQUE (email_contato)
                )';
            EXCEPTION
                WHEN OTHERS THEN
                    IF SQLCODE != -955 THEN
                        RAISE;
                    END IF;
            END;
            """
        )
        logging.info('Tabela empresas verificada/criada.')

        # Criar tabela usuarios
        cur.execute(
            """
            BEGIN
                EXECUTE IMMEDIATE '
                CREATE TABLE usuarios (
                    id_usuario NUMBER(6) NOT NULL,
                    id_empresa NUMBER(6),
                    nome_completo VARCHAR2(60) NOT NULL,
                    email VARCHAR2(60) NOT NULL,
                    senha_hash VARCHAR2(80) NOT NULL,
                    nivel_carreira VARCHAR2(30) NOT NULL,
                    ocupacao VARCHAR2(30) NOT NULL,
                    genero VARCHAR2(15) NOT NULL,
                    data_nascimento DATE,
                    data_cadastro TIMESTAMP WITH TIME ZONE DEFAULT SYSTIMESTAMP NOT NULL,
                    is_admin NUMBER(1) DEFAULT 0 NOT NULL,
                    CONSTRAINT usuarios_PK PRIMARY KEY (id_usuario),
                    CONSTRAINT usuarios_email_uk UNIQUE (email),
                    CONSTRAINT usuarios_empresas_FK FOREIGN KEY (id_empresa) REFERENCES empresas(id_empresa)
                )';
            EXCEPTION
                WHEN OTHERS THEN
                    IF SQLCODE != -955 THEN
                        RAISE;
                    END IF;
            END;
            """
        )
        logging.info('Tabela usuarios verificada/criada.')

        # Criar sequence com START baseado em MAX(id_usuario) existente
        try:
            # Verifica MAX(id_usuario) existente
            cur.execute('SELECT NVL(MAX(id_usuario), 0) + 1 FROM usuarios')
            start_val = cur.fetchone()[0]

            cur.execute(
                f"""
                BEGIN
                    EXECUTE IMMEDIATE 'CREATE SEQUENCE usuarios_seq START WITH {start_val} INCREMENT BY 1 NOCACHE';
                EXCEPTION
                    WHEN OTHERS THEN
                        IF SQLCODE != -955 THEN
                            RAISE;
                        END IF;
                END;
                """
            )
            logging.info(
                f'Sequence usuarios_seq verificada/criada (START={start_val}).'
            )
        except Exception as e:
            logging.warning(f'Aviso ao criar sequence: {e}')

        conn.commit()
    except Exception as e:
        logging.error(f'Erro em init_table: {e}')
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


# As funções específicas de usuário foram separadas para `usuario_dao.py` para
# manter responsabilidade única por entidade.
from contextlib import contextmanager


@contextmanager
def get_cursor(conn_info: Dict = None):
    conn = _connect(conn_info)
    cur = conn.cursor()
    try:
        yield cur
    finally:
        cur.close()
        conn.close()
