from typing import Dict


def list_empresas(conn_info: Dict = None):
    """Retorna lista de empresas (id_empresa, nome_empresa)."""
    conn = _connect(conn_info)
    cur = conn.cursor()
    try:
        cur.execute("SELECT id_empresa, nome_empresa FROM empresas ORDER BY id_empresa")
        empresas = cur.fetchall()
        return empresas
    except Exception as e:
        logging.error(f'Erro ao listar empresas: {e}')
        return []
    finally:
        cur.close()
        conn.close()
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

    Quem usar esta função deve fechar a conexão com `conn.close()` quando terminar.
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
        # Criar tabela empresas (definição conforme README)
        cur.execute(
            """
            BEGIN
                EXECUTE IMMEDIATE '
                CREATE TABLE empresas (
                    id_empresa NUMBER(6) NOT NULL,
                    nome_empresa VARCHAR2(60) NOT NULL,
                    cnpj VARCHAR2(18) NOT NULL,
                    email_contato VARCHAR2(60) NOT NULL,
                    data_cadastro TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL,
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

        # Criar tabela usuarios (definição conforme README)
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
                    data_nascimento DATE NOT NULL,
                    data_cadastro TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL,
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

        # Criar tabela trilhas
        cur.execute(
            """
            BEGIN
                EXECUTE IMMEDIATE '
                CREATE TABLE trilhas (
                    id_trilha NUMBER(6) NOT NULL,
                    nome_trilha VARCHAR2(40) NOT NULL,
                    descricao_trilha VARCHAR2(400) NOT NULL,
                    imagem_trilha BLOB,
                    imagem_trilha_nome VARCHAR2(255),
                    imagem_trilha_mime VARCHAR2(100),
                    imagem_trilha_tamanho NUMBER(10),
                    imagem_trilha_alt VARCHAR2(200),
                    imagem_trilha_thumb BLOB,
                    categoria VARCHAR2(30) NOT NULL,
                    nivel_dificuldade VARCHAR2(15) NOT NULL,
                    data_criacao TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL,
                    CONSTRAINT trilhas_PK PRIMARY KEY (id_trilha),
                    CONSTRAINT ck_nivel_dificuldade CHECK (nivel_dificuldade IN (''Iniciante'', ''Intermediário'', ''Avançado''))
                )';
            EXCEPTION
                WHEN OTHERS THEN
                    IF SQLCODE != -955 THEN
                        RAISE;
                    END IF;
            END;
            """
        )
        logging.info('Tabela trilhas verificada/criada.')

        # Criar tabela cursos
        cur.execute(
            """
            BEGIN
                EXECUTE IMMEDIATE '
                CREATE TABLE cursos (
                    id_curso NUMBER(6) NOT NULL,
                    id_trilha NUMBER(6) NOT NULL,
                    titulo VARCHAR2(80) NOT NULL,
                    descricao_curso VARCHAR2(400) NOT NULL,
                    imagem_curso BLOB,
                    imagem_curso_nome VARCHAR2(255),
                    imagem_curso_mime VARCHAR2(100),
                    imagem_curso_tamanho NUMBER(10),
                    imagem_curso_alt VARCHAR2(200),
                    imagem_curso_thumb BLOB,
                    plataforma VARCHAR2(30) NOT NULL,
                    link_curso VARCHAR2(500) NOT NULL,
                    duracao_horas NUMBER(3) NOT NULL,
                    CONSTRAINT cursos_PK PRIMARY KEY (id_curso),
                    CONSTRAINT cursos_link_curso_uk UNIQUE (link_curso),
                    CONSTRAINT cursos_trilhas_FK FOREIGN KEY (id_trilha) REFERENCES trilhas(id_trilha),
                    CONSTRAINT ck_duracao_horas CHECK (duracao_horas > 0)
                )';
            EXCEPTION
                WHEN OTHERS THEN
                    IF SQLCODE != -955 THEN
                        RAISE;
                    END IF;
            END;
            """
        )
        logging.info('Tabela cursos verificada/criada.')

        # Criar tabela usuario_trilha
        cur.execute(
            """
            BEGIN
                EXECUTE IMMEDIATE '
                CREATE TABLE usuario_trilha (
                    id_usuario NUMBER(6) NOT NULL,
                    id_trilha NUMBER(6) NOT NULL,
                    data_inicio TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL,
                    progresso_percentual NUMBER(3) NOT NULL,
                    status VARCHAR2(15) NOT NULL,
                    CONSTRAINT usuario_trilha_PK PRIMARY KEY (id_usuario, id_trilha),
                    CONSTRAINT usuario_trilha_usuarios_FK FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
                    CONSTRAINT usuario_trilha_trilhas_FK FOREIGN KEY (id_trilha) REFERENCES trilhas(id_trilha),
                    CONSTRAINT ck_progresso_percentual CHECK (progresso_percentual BETWEEN 0 AND 100)
                )';
            EXCEPTION
                WHEN OTHERS THEN
                    IF SQLCODE != -955 THEN
                        RAISE;
                    END IF;
            END;
            """
        )
        logging.info('Tabela usuario_trilha verificada/criada.')

        # Criar tabela bem_estar
        cur.execute(
            """
            BEGIN
                EXECUTE IMMEDIATE '
                CREATE TABLE bem_estar (
                    id_registro NUMBER(8) NOT NULL,
                    id_usuario NUMBER(6) NOT NULL,
                    data_registro TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL,
                    nivel_estresse NUMBER(2) NOT NULL,
                    nivel_motivacao NUMBER(2) NOT NULL,
                    qualidade_sono NUMBER(2) NOT NULL,
                    observacao VARCHAR2(200),
                    CONSTRAINT bem_estar_PK PRIMARY KEY (id_registro),
                    CONSTRAINT bem_estar_usuarios_FK FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
                    CONSTRAINT ck_nivel_estresse CHECK (nivel_estresse BETWEEN 0 AND 10),
                    CONSTRAINT ck_nivel_motivacao CHECK (nivel_motivacao BETWEEN 0 AND 10),
                    CONSTRAINT ck_qualidade_sono CHECK (qualidade_sono BETWEEN 0 AND 10)
                )';
            EXCEPTION
                WHEN OTHERS THEN
                    IF SQLCODE != -955 THEN
                        RAISE;
                    END IF;
            END;
            """
        )
        logging.info('Tabela bem_estar verificada/criada.')

        # Criar tabela recomendacoes
        cur.execute(
            """
            BEGIN
                EXECUTE IMMEDIATE '
                CREATE TABLE recomendacoes (
                    id_recomendacao NUMBER(8) NOT NULL,
                    id_usuario NUMBER(6) NOT NULL,
                    tipo VARCHAR2(7) NOT NULL,
                    id_referencia NUMBER(6) NOT NULL,
                    motivo VARCHAR2(120) NOT NULL,
                    data_recomendacao TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL,
                    CONSTRAINT recomendacoes_PK PRIMARY KEY (id_recomendacao),
                    CONSTRAINT recomendacoes_usuarios_FK FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
                    CONSTRAINT ck_tipo_recomendacao CHECK (tipo IN (''Curso'', ''Trilha''))
                )';
            EXCEPTION
                WHEN OTHERS THEN
                    IF SQLCODE != -955 THEN
                        RAISE;
                    END IF;
            END;
            """
        )
        logging.info('Tabela recomendacoes verificada/criada.')

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
