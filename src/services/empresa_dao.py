"""
Operações de persistência para a entidade `empresas`.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional

from .DAO import _connect
from .exceptions import DatabaseError

logger = logging.getLogger(__name__)


def _rows_to_dicts(cursor) -> List[Dict]:
    cols = [c[0].lower() for c in cursor.description]
    rows = cursor.fetchall()
    results: List[Dict] = []
    for r in rows:
        d: Dict = {}
        for k, v in zip(cols, r):
            try:
                if isinstance(v, (datetime,)):
                    d[k] = v.isoformat()
                else:
                    d[k] = v
            except Exception:
                d[k] = str(v)
        results.append(d)
    return results


def insert_empresa(empresa: Dict, conn_info: Dict = None) -> int:
    if not empresa.get('nome_empresa'):
        raise ValueError('nome_empresa é obrigatório')
    if not empresa.get('cnpj'):
        raise ValueError('cnpj é obrigatório')
    if not empresa.get('email_contato'):
        raise ValueError('email_contato é obrigatório')

    conn = _connect(conn_info)
    cur = conn.cursor()
    try:
        try:
            cur.execute('SELECT empresas_seq.NEXTVAL FROM dual')
            next_id = cur.fetchone()[0]
        except Exception as e:
            logger.warning(f'Sequence empresas_seq não disponível, usando MAX+1: {e}')
            cur.execute('SELECT NVL(MAX(id_empresa),0) + 1 FROM empresas')
            next_id = cur.fetchone()[0]

        cur.execute(
            'INSERT INTO empresas (id_empresa, nome_empresa, cnpj, email_contato) VALUES (:1,:2,:3,:4)',
            (
                next_id,
                empresa.get('nome_empresa'),
                empresa.get('cnpj'),
                empresa.get('email_contato'),
            ),
        )
        conn.commit()
        logger.info(f'Empresa inserida com sucesso: id={next_id}, nome={empresa.get("nome_empresa")}')
        return next_id
    except Exception as e:
        conn.rollback()
        logger.error(f'Erro ao inserir empresa: {e}')
        raise DatabaseError('Erro ao inserir empresa') from e
    finally:
        cur.close()
        conn.close()


def get_empresa_por_id(id_empresa: int, conn_info: Dict = None) -> Optional[Dict]:
    conn = _connect(conn_info)
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT id_empresa, nome_empresa, cnpj, email_contato,
                   TO_CHAR(data_cadastro, 'YYYY-MM-DD"T"HH24:MI:SS TZH:TZM') AS data_cadastro
            FROM empresas
            WHERE id_empresa = :1
            """,
            (id_empresa,),
        )
        rows = _rows_to_dicts(cur)
        return rows[0] if rows else None
    except Exception as e:
        logger.error(f'Erro ao consultar empresa {id_empresa}: {e}')
        raise DatabaseError('Erro ao consultar empresa') from e
    finally:
        cur.close()
        conn.close()


def list_empresas(conn_info: Dict = None) -> List[Dict]:
    conn = _connect(conn_info)
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT id_empresa, nome_empresa, cnpj, email_contato,
                   TO_CHAR(data_cadastro, 'YYYY-MM-DD"T"HH24:MI:SS TZH:TZM') AS data_cadastro
            FROM empresas
            ORDER BY id_empresa
            """
        )
        return _rows_to_dicts(cur)
    except Exception as e:
        logger.error(f'Erro ao listar empresas: {e}')
        raise DatabaseError('Erro ao listar empresas') from e
    finally:
        cur.close()
        conn.close()


def update_empresa(id_empresa: int, empresa: Dict, conn_info: Dict = None) -> None:
    conn = _connect(conn_info)
    cur = conn.cursor()
    try:
        cur.execute(
            'UPDATE empresas SET nome_empresa = :1, cnpj = :2, email_contato = :3 WHERE id_empresa = :4',
            (
                empresa.get('nome_empresa'),
                empresa.get('cnpj'),
                empresa.get('email_contato'),
                id_empresa,
            ),
        )
        conn.commit()
        logger.info(f'Empresa atualizada: id={id_empresa}')
    except Exception as e:
        conn.rollback()
        logger.error(f'Erro ao atualizar empresa {id_empresa}: {e}')
        raise DatabaseError('Erro ao atualizar empresa') from e
    finally:
        cur.close()
        conn.close()


def delete_empresa(id_empresa: int, conn_info: Dict = None) -> None:
    conn = _connect(conn_info)
    cur = conn.cursor()
    try:
        cur.execute('DELETE FROM empresas WHERE id_empresa = :1', (id_empresa,))
        if cur.rowcount == 0:
            logger.warning(f'Nenhuma empresa encontrada com id={id_empresa}')
        else:
            logger.info(f'Empresa removida: id={id_empresa}')
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f'Erro ao deletar empresa {id_empresa}: {e}')
        raise DatabaseError('Erro ao deletar empresa') from e
    finally:
        cur.close()
        conn.close()


def cnpj_ou_email_existe(cnpj: str = None, email_contato: str = None, exclude_id: int = None, conn_info: Dict = None) -> bool:
    conn = _connect(conn_info)
    cur = conn.cursor()
    try:
        if cnpj:
            if exclude_id:
                cur.execute('SELECT COUNT(1) FROM empresas WHERE cnpj = :1 AND id_empresa <> :2', (cnpj, exclude_id))
            else:
                cur.execute('SELECT COUNT(1) FROM empresas WHERE cnpj = :1', (cnpj,))
            if cur.fetchone()[0] > 0:
                return True
        if email_contato:
            if exclude_id:
                cur.execute('SELECT COUNT(1) FROM empresas WHERE email_contato = :1 AND id_empresa <> :2', (email_contato, exclude_id))
            else:
                cur.execute('SELECT COUNT(1) FROM empresas WHERE email_contato = :1', (email_contato,))
            if cur.fetchone()[0] > 0:
                return True
        return False
    except Exception as e:
        logger.error(f'Erro ao verificar cnpj/email: {e}')
        raise DatabaseError('Erro ao verificar cnpj/email') from e
    finally:
        cur.close()
        conn.close()
