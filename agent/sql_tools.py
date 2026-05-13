import os
import psycopg2
from langchain_community.utilities import SQLDatabase

_PG_DSN = os.getenv("PG_DSN", "host=postgres port=5432 user=superagente password=superagente dbname=superagente")


def _pg_dsn_to_uri(dsn):
    parts = dict(p.split("=", 1) for p in dsn.split() if "=" in p)
    return (
        f"postgresql://{parts.get('user', 'superagente')}"
        f":{parts.get('password', '')}"
        f"@{parts.get('host', 'localhost')}"
        f":{parts.get('port', '5432')}"
        f"/{parts.get('dbname', 'superagente')}"
    )


_db = None


def _get_db():
    global _db
    if _db is None:
        _db = SQLDatabase.from_uri(_pg_dsn_to_uri(_PG_DSN))
    return _db


def list_tables():
    """Retorna lista de tablas disponibles."""
    return _get_db().get_usable_table_names()


def get_schema(table_name=None):
    """Retorna el esquema de una o todas las tablas."""
    db = _get_db()
    if table_name:
        return db.get_table_info([table_name])
    return db.get_table_info()


def check_query(sql):
    """Valida sintaxis SQL con EXPLAIN. Retorna None si es válido, o el error."""
    conn = psycopg2.connect(_PG_DSN)
    conn.autocommit = True
    cur = conn.cursor()
    try:
        cur.execute(f"EXPLAIN {sql}")
        cur.fetchall()
        return None
    except Exception as e:
        msg = str(e).split("\n")[0].replace("ERROR: ", "").strip()
        return msg
    finally:
        cur.close()
        conn.close()


def execute_query(sql, limit=100):
    """Ejecuta SELECT y retorna filas como lista de dicts."""
    upper = sql.strip().upper()
    if not upper.startswith("SELECT") and not upper.startswith("WITH"):
        return "Error: solo SELECT"
    conn = psycopg2.connect(_PG_DSN)
    conn.autocommit = True
    cur = conn.cursor()
    try:
        cur.execute(sql)
        cols = [d[0] for d in cur.description]
        rows = [dict(zip(cols, r)) for r in cur.fetchmany(limit)]
        return rows
    except Exception as e:
        return f"Error: {e}"
    finally:
        cur.close()
        conn.close()


def build_schema_context(tables=None):
    available = list_tables()
    if tables:
        target = [t for t in tables if t in available]
    else:
        target = available

    ctx = _get_db().get_table_info(target)

    rules = (
        "\n\nFunciones PostgreSQL: SUM, COUNT, AVG, MIN, MAX, EXTRACT, TO_CHAR, ROUND\n"
        "  - EXTRACT(YEAR FROM fecha) para año\n"
        "  - EXTRACT(MONTH FROM fecha) para mes\n"
        "  - EXTRACT(QUARTER FROM fecha) para trimestre\n"
        "  - CASE WHEN EXTRACT(MONTH FROM fecha) <= 6 THEN 1 ELSE 2 END para semestre\n"
        "  - TO_CHAR(fecha, 'YYYY-MM-DD') para fechas\n"
        "Reglas:\n"
        "- Solo SELECT. Repite expresión en GROUP BY, no alias.\n"
        "- Proyecciones: promedio mensual × meses\n"
        "- Responde ÚNICAMENTE con SQL"
    )
    return ctx + rules
