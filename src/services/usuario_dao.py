"""
Operações de persistência para a entidade `usuarios`.
"""

import logging
from datetime import date, datetime
from typing import Dict, List, Optional

from .DAO import _connect

logging.getLogger(__name__)


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


def insert_usuario(usuario: Dict, conn_info: Dict = None) -> int:
    if not usuario.get('nome_completo'):
        raise ValueError('nome_completo é obrigatório')
    if not usuario.get('email'):
        raise ValueError('email é obrigatório')
    if not usuario.get('senha_hash'):
        raise ValueError('senha_hash é obrigatório')

    if not usuario.get('nivel_carreira'):
        usuario['nivel_carreira'] = 'Não especificado'
    if not usuario.get('ocupacao'):
        usuario['ocupacao'] = 'Não especificado'
    if not usuario.get('genero'):
        usuario['genero'] = 'Não especificado'

    id_empresa = usuario.get('id_empresa')
    if id_empresa in ('', None):
        id_empresa = None
    elif not isinstance(id_empresa, int):
        try:
            id_empresa = int(id_empresa)
        except Exception:
            id_empresa = None
    usuario['id_empresa'] = id_empresa

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
        dn_val = None

        if isinstance(dn, str):
            if dn.strip():
                for fmt in ('%Y-%m-%d', '%d/%m/%Y'):
                    try:
                        dn_val = datetime.strptime(dn, fmt).date()
                        break
                    except Exception:
                        continue
        elif isinstance(dn, date):
            dn_val = dn

        if dn_val is None:
            dn_val = date(1900, 1, 1)
            logging.warning(
                'Data de nascimento não fornecida, usando data padrão: 01/01/1900'
            )

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


def get_usuario_por_id(id_usuario: int, conn_info: Dict = None) -> Optional[Dict]:
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
        dn_val = None

        if isinstance(dn, str):
            if not dn.strip():
                cur.execute(
                    'SELECT data_nascimento FROM usuarios WHERE id_usuario = :1',
                    (id_usuario,),
                )
                row = cur.fetchone()
                dn_val = row[0] if row else None
            else:
                for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%Y-%m-%dT%H:%M:%S'):
                    try:
                        dn_val = datetime.strptime(dn, fmt).date()
                        break
                    except Exception:
                        continue
        elif isinstance(dn, date):
            dn_val = dn
        elif dn is None:
            cur.execute(
                'SELECT data_nascimento FROM usuarios WHERE id_usuario = :1',
                (id_usuario,),
            )
            row = cur.fetchone()
            dn_val = row[0] if row else None

        if dn_val is None:
            dn_val = date(1900, 1, 1)
            logging.warning(
                f'Data de nascimento NULL para usuário {id_usuario}, usando data padrão: 01/01/1900'
            )

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
