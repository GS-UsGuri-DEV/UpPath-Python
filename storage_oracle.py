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

import os
from datetime import date, datetime
from typing import Dict, List, Optional
import oracledb


def _connect(conn_info: Dict = None):
    if oracledb is None:
        raise ModuleNotFoundError('oracledb não encontrado')
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
    """Tenta criar a tabela `usuarios`, `empresas` se não existir (ignora erro se existir)."""
    conn = _connect(conn_info)
    cur = conn.cursor()
    try:
        cur.execute(
            """
            BEGIN
                EXECUTE IMMEDIATE '
                CREATE TABLE empresas (
                    id_empresa NUMBER(6) NOT NULL,
                    nome_empresa VARCHAR2(60) NOT NULL,
                    cnpj VARCHAR2(18) NOT NULL,
                    email_contato VARCHAR2(60) NOT NULL,
                    data_cadastro TIMESTAMP WITH TIME ZONE DEFAULT (SYSTIMESTAMP AT TIME ZONE ''America/Sao_Paulo'') NOT NULL,
                    CONSTRAINT empresas_PK PRIMARY KEY (id_empresa),
                    CONSTRAINT empresas_cnpj_uk UNIQUE (cnpj),
                    CONSTRAINT empresas_email_uk UNIQUE (email_contato)
                )';
            EXCEPTION
                WHEN OTHERS THEN
                    NULL;
            END;
            """
        )
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
                    data_cadastro TIMESTAMP WITH TIME ZONE DEFAULT (SYSTIMESTAMP AT TIME ZONE ''America/Sao_Paulo'') NOT NULL,
                    is_admin NUMBER(1) DEFAULT 0 NOT NULL,
                    CONSTRAINT usuarios_PK PRIMARY KEY (id_usuario),
                    CONSTRAINT usuarios_email_uk UNIQUE (email),
                    CONSTRAINT usuarios_empresas_FK FOREIGN KEY (id_empresa) REFERENCES empresas(id_empresa)
                )';
            EXCEPTION
                WHEN OTHERS THEN
                    NULL;
            END;
            """
        )
        # tenta criar uma sequência para id autoincrement
        try:
            cur.execute(
                """
                BEGIN
                    EXECUTE IMMEDIATE 'CREATE SEQUENCE usuarios_seq START WITH 1 INCREMENT BY 1 NOCACHE';
                EXCEPTION
                    WHEN OTHERS THEN
                        NULL;
                END;
                """
            )
        except Exception:
            pass
        conn.commit()
    except Exception:
        pass
    finally:
        cur.close()
        conn.close()


def insert_usuario(usuario: Dict, conn_info: Dict = None) -> int:
    """Insere um usuário e retorna o `id_usuario` criado.

    `usuario` deve ser um dict com chaves: id_empresa, nome_completo, email,
    senha_hash, nivel_carreira, ocupacao, genero, data_nascimento (date or ISO-str), is_admin
    """
    init_table(conn_info)
    conn = _connect(conn_info)
    cur = conn.cursor()
    try:
        try:
            cur.execute('SELECT usuarios_seq.NEXTVAL FROM dual')
            next_id = cur.fetchone()[0]
        except Exception:
            # fallback para NVL(MAX(...))+1 se a sequência não estiver disponível
            cur.execute('SELECT NVL(MAX(id_usuario),0) + 1 FROM usuarios')
            next_id = cur.fetchone()[0]

        dn = usuario.get('data_nascimento')
        if isinstance(dn, str):
            try:
                dn_val = datetime.strptime(dn, '%Y-%m-%d').date()
            except Exception:
                dn_val = None
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
                usuario.get('nivel_carreira') or '',
                usuario.get('ocupacao') or '',
                usuario.get('genero') or '',
                dn_val,
                usuario.get('is_admin') or 0,
            ),
        )
        conn.commit()
        return next_id
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
        cur.execute('SELECT * FROM usuarios WHERE id_usuario = :1', (id_usuario,))
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
        cur.execute('SELECT * FROM usuarios ORDER BY id_usuario')
        return _rows_to_dicts(cur)
    finally:
        cur.close()
        conn.close()


def update_usuario(id_usuario: int, usuario: Dict, conn_info: Dict = None) -> None:
    """Atualiza o registro do usuário com `id_usuario` com os campos do dict `usuario`."""
    conn = _connect(conn_info)
    cur = conn.cursor()
    try:
        dn = usuario.get('data_nascimento')
        if isinstance(dn, str):
            try:
                dn_val = datetime.strptime(dn, '%Y-%m-%d').date()
            except Exception:
                dn_val = None
        else:
            dn_val = dn
        cur.execute(
            'UPDATE usuarios SET id_empresa = :1, nome_completo = :2, email = :3, senha_hash = :4, nivel_carreira = :5, ocupacao = :6, genero = :7, data_nascimento = :8, is_admin = :9 WHERE id_usuario = :10',
            (
                usuario.get('id_empresa'),
                usuario.get('nome_completo'),
                usuario.get('email'),
                usuario.get('senha_hash'),
                usuario.get('nivel_carreira') or '',
                usuario.get('ocupacao') or '',
                usuario.get('genero') or '',
                dn_val,
                usuario.get('is_admin') or 0,
                id_usuario,
            ),
        )
        conn.commit()
    finally:
        cur.close()
        conn.close()


def delete_usuario(id_usuario: int, conn_info: Dict = None) -> None:
    conn = _connect(conn_info)
    cur = conn.cursor()
    try:
        cur.execute('DELETE FROM usuarios WHERE id_usuario = :1', (id_usuario,))
        conn.commit()
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
