"""
storage_oracle.py

Camada leve para sincronizar `usuarios.json` com um banco Oracle e executar
consultas. Usa o driver `oracledb` (ou `cx_Oracle` compatível). Este módulo
é opcional — se não estiver instalado, o código chamador deve tratar a
ausência.

Configuração de conexão (válida se não passar `conn_info`):
- Variáveis de ambiente: ORACLE_USER, ORACLE_PASSWORD, ORACLE_DSN

Observação: operações de escrita (sync) recriam os registros na tabela
`usuarios`. A criação da tabela é tentada e erros são ignorados quando a
tabela já existe.
"""

import logging
import os
from datetime import date, datetime
from typing import Dict, List, Optional

try:
    import oracledb
except ImportError:
    oracledb = None

# Pool de conexões global (opcional)
_connection_pool = None

logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s'
)


def init_pool(
    min_connections: int = 2, max_connections: int = 10, conn_info: Dict = None
):
    """Inicializa pool de conexões para melhor performance."""
    global _connection_pool
    if oracledb is None:
        raise ModuleNotFoundError('oracledb não encontrado')
    if _connection_pool is not None:
        logging.info('Pool de conexões já inicializado.')
        return

    if conn_info is None:
        user = os.getenv('ORACLE_USER')
        password = os.getenv('ORACLE_PASSWORD')
        dsn = os.getenv('ORACLE_DSN')
    else:
        user = conn_info.get('user')
        password = conn_info.get('password')
        dsn = conn_info.get('dsn')

    if not (user and password and dsn):
        raise ValueError('Informação de conexão Oracle incompleta')

    try:
        _connection_pool = oracledb.create_pool(
            user=user,
            password=password,
            dsn=dsn,
            min=min_connections,
            max=max_connections,
        )
        logging.info(
            f'Pool de conexões criado (min={min_connections}, max={max_connections})'
        )
    except Exception as e:
        logging.error(f'Erro ao criar pool de conexões: {e}')
        raise


def _connect(conn_info: Dict = None):
    """Obtém conexão do pool (se disponível) ou cria conexão direta."""
    global _connection_pool
    if oracledb is None:
        raise ModuleNotFoundError('oracledb não encontrado')

    # Usa pool se disponível
    if _connection_pool is not None:
        return _connection_pool.acquire()

    # Conexão direta
    if conn_info is None:
        user = os.getenv('ORACLE_USER')
        password = os.getenv('ORACLE_PASSWORD')
        dsn = os.getenv('ORACLE_DSN')
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


def insert_usuario(usuario: Dict, conn_info: Dict = None) -> int:
    """Insere um usuário e retorna o `id_usuario` criado.

    `usuario` deve ser um dict com chaves: id_empresa, nome_completo, email,
    senha_hash, nivel_carreira, ocupacao, genero, data_nascimento (date or ISO-str), is_admin
    """
    # Validação básica de campos obrigatórios
    if not usuario.get('nome_completo'):
        raise ValueError('nome_completo é obrigatório')
    if not usuario.get('email'):
        raise ValueError('email é obrigatório')
    if not usuario.get('senha_hash'):
        raise ValueError('senha_hash é obrigatório')

    # Garantir valores default para campos NOT NULL
    if not usuario.get('nivel_carreira'):
        usuario['nivel_carreira'] = 'Não especificado'
    if not usuario.get('ocupacao'):
        usuario['ocupacao'] = 'Não especificado'
    if not usuario.get('genero'):
        usuario['genero'] = 'Não especificado'

    # Defensive: id_empresa must be int or None
    id_empresa = usuario.get('id_empresa')
    if id_empresa in ('', None):
        id_empresa = None
    elif not isinstance(id_empresa, int):
        try:
            id_empresa = int(id_empresa)
        except Exception:
            id_empresa = None
    usuario['id_empresa'] = id_empresa

    # Defensive: is_admin must be int (0 or 1)
    is_admin = usuario.get('is_admin')
    if is_admin in ('', None):
        is_admin = 0
    elif not isinstance(is_admin, int):
        try:
            is_admin = int(is_admin)
        except Exception:
            is_admin = 0
    usuario['is_admin'] = is_admin

    conn = _connect(conn_info)
    cur = conn.cursor()
    try:
        try:
            cur.execute('SELECT usuarios_seq.NEXTVAL FROM dual')
            next_id = cur.fetchone()[0]
        except Exception as e:
            logging.warning(f'Sequence não disponível, usando MAX+1: {e}')
            cur.execute('SELECT NVL(MAX(id_usuario),0) + 1 FROM usuarios')
            next_id = cur.fetchone()[0]

        dn = usuario.get('data_nascimento')
        if isinstance(dn, str):
            dn_val = None
            for fmt in ('%Y-%m-%d', '%d/%m/%Y'):
                try:
                    dn_val = datetime.strptime(dn, fmt).date()
                    break
                except Exception:
                    continue
        else:
            dn_val = dn

        cur.execute(
            'INSERT INTO usuarios (id_usuario, id_empresa, nome_completo, email, senha_hash, nivel_carreira, ocupacao, genero, data_nascimento, is_admin) VALUES (:1,:2,:3,:4,:5,:6,:7,:8,:9,:10)',
            (
                next_id,
                usuario.get('id_empresa'),
                usuario.get('nome_completo'),
                usuario.get('email'),
                usuario.get('senha_hash'),
                usuario.get('nivel_carreira'),
                usuario.get('ocupacao'),
                usuario.get('genero'),
                dn_val,
                usuario.get('is_admin') or 0,
            ),
        )
        conn.commit()
        logging.info(
            f'Usuário inserido com sucesso: id={next_id}, email={usuario.get("email")}'
        )
        return next_id
    except Exception as e:
        conn.rollback()
        logging.error(f'Erro ao inserir usuário: {e}')
        raise
    finally:
        cur.close()
        conn.close()


def _rows_to_dicts(cursor) -> List[Dict]:
    cols = [c[0].lower() for c in cursor.description]
    rows = cursor.fetchall()
    results: List[Dict] = []
    for r in rows:
        d: Dict = {}
        for k, v in zip(cols, r):
            if isinstance(v, (date, datetime)):
                try:
                    d[k] = v.isoformat()
                except Exception:
                    d[k] = str(v)
            else:
                d[k] = v
        results.append(d)
    return results


def get_usuario_por_id(id_usuario: int, conn_info: Dict = None) -> Optional[Dict]:
    """Retorna um dicionário do usuário ou None se não encontrado."""
    conn = _connect(conn_info)
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT id_usuario, id_empresa, nome_completo, email, senha_hash,
                   nivel_carreira, ocupacao, genero, data_nascimento,
                   TO_CHAR(data_cadastro, 'YYYY-MM-DD"T"HH24:MI:SS TZH:TZM') AS data_cadastro,
                   is_admin
            FROM usuarios
            WHERE id_usuario = :1
            """,
            (id_usuario,),
        )
        rows = _rows_to_dicts(cur)
        return rows[0] if rows else None
    finally:
        cur.close()
        conn.close()


def list_usuarios(conn_info: Dict = None) -> List[Dict]:
    """Retorna lista de usuários como dicionários (ordem por id)."""
    conn = _connect(conn_info)
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT id_usuario, id_empresa, nome_completo, email, senha_hash,
                   nivel_carreira, ocupacao, genero, data_nascimento,
                   TO_CHAR(data_cadastro, 'YYYY-MM-DD"T"HH24:MI:SS TZH:TZM') AS data_cadastro,
                   is_admin
            FROM usuarios
            ORDER BY id_usuario
            """
        )
        return _rows_to_dicts(cur)
    finally:
        cur.close()
        conn.close()


def update_usuario(id_usuario: int, usuario: Dict, conn_info: Dict = None) -> None:
    """Atualiza o registro do usuário com `id_usuario` com os campos do dict `usuario`."""
    # Garantir valores default para campos NOT NULL
    if not usuario.get('nivel_carreira'):
        usuario['nivel_carreira'] = 'Não especificado'
    if not usuario.get('ocupacao'):
        usuario['ocupacao'] = 'Não especificado'
    if not usuario.get('genero'):
        usuario['genero'] = 'Não especificado'

    conn = _connect(conn_info)
    cur = conn.cursor()
    try:
        dn = usuario.get('data_nascimento')
        if isinstance(dn, str):
            dn_val = None
            for fmt in ('%Y-%m-%d', '%d/%m/%Y'):
                try:
                    dn_val = datetime.strptime(dn, fmt).date()
                    break
                except Exception:
                    continue
        else:
            dn_val = dn
        cur.execute(
            'UPDATE usuarios SET id_empresa = :1, nome_completo = :2, email = :3, senha_hash = :4, nivel_carreira = :5, ocupacao = :6, genero = :7, data_nascimento = :8, is_admin = :9 WHERE id_usuario = :10',
            (
                usuario.get('id_empresa'),
                usuario.get('nome_completo'),
                usuario.get('email'),
                usuario.get('senha_hash'),
                usuario.get('nivel_carreira'),
                usuario.get('ocupacao'),
                usuario.get('genero'),
                dn_val,
                usuario.get('is_admin') or 0,
                id_usuario,
            ),
        )
        conn.commit()
        logging.info(f'Usuário atualizado: id={id_usuario}')
    except Exception as e:
        conn.rollback()
        logging.error(f'Erro ao atualizar usuário {id_usuario}: {e}')
        raise
    finally:
        cur.close()
        conn.close()


def delete_usuario(id_usuario: int, conn_info: Dict = None) -> None:
    """Remove um usuário do banco de dados."""
    conn = _connect(conn_info)
    cur = conn.cursor()
    try:
        cur.execute('DELETE FROM usuarios WHERE id_usuario = :1', (id_usuario,))
        if cur.rowcount == 0:
            logging.warning(f'Nenhum usuário encontrado com id={id_usuario}')
        else:
            logging.info(f'Usuário removido: id={id_usuario}')
        conn.commit()
    except Exception as e:
        conn.rollback()
        logging.error(f'Erro ao deletar usuário {id_usuario}: {e}')
        raise
    finally:
        cur.close()
        conn.close()


def email_existe(email: str, exclude_id: int = None, conn_info: Dict = None) -> bool:
    conn = _connect(conn_info)
    cur = conn.cursor()
    try:
        if exclude_id:
            cur.execute(
                'SELECT COUNT(1) FROM usuarios WHERE email = :1 AND id_usuario <> :2',
                (email, exclude_id),
            )
        else:
            cur.execute('SELECT COUNT(1) FROM usuarios WHERE email = :1', (email,))
        return cur.fetchone()[0] > 0
    finally:
        cur.close()
        conn.close()
