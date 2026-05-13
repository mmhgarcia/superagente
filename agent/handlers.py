import os
import re
import psycopg2
from .sql_tools import build_schema_context

PG_DSN = os.getenv("PG_DSN", "host=postgres port=5432 user=superagente password=superagente dbname=superagente")


def _get_conn():
    return psycopg2.connect(PG_DSN)


def _query(sql):
    conn = _get_conn()
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(sql)
    cols = [d[0] for d in cur.description]
    rows = [dict(zip(cols, r)) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return rows


def _validate_sql(sql):
    conn = _get_conn()
    conn.autocommit = True
    cur = conn.cursor()
    try:
        cur.execute(f"EXPLAIN {sql}")
        cur.fetchall()
        return None
    except Exception as e:
        msg = str(e)
        clean = msg.split("\n")[0]
        clean = clean.replace("ERROR: ", "").strip()
        return clean
    finally:
        cur.close()
        conn.close()


def _get_schema():
    return build_schema_context()


def sql_handler(message):
    from .llm import generate
    sql = None
    error = None

    for attempt in range(3):
        schema = _get_schema()
        if attempt == 0:
            raw = generate(message, system_prompt=schema)
        else:
            raw = generate(
                _FIX_PROMPT.format(error=error, sql=sql),
                system_prompt=schema,
            )
        if not raw:
            return "El LLM no respondió."

        sql = _strip_sql(raw)
        if not _es_select_valido(sql):
            return f"SQL no válido (solo SELECT): {sql[:100]}"

        error = _validate_sql(sql)
        if not error:
            break

    if error:
        return f"SQL inválido tras {3} intentos: {error}"

    try:
        data = _query(sql)
    except Exception as e:
        return f"Error ejecutando SQL: {e}"
    if not data:
        return "No se encontraron resultados."
    cols = list(data[0].keys())
    lines = [" | ".join(cols), "-" * (len(cols) * 8)]
    for row in data:
        lines.append(" | ".join(str(row[c]) for c in cols))
    return "\n".join(lines)


_FIX_PROMPT = (
    "El SQL que generaste tiene un error de PostgreSQL. Corrígelo.\n\n"
    "Error: {error}\n\n"
    "SQL erróneo:\n{sql}\n\n"
    "Regla CRÍTICA para PostgreSQL: NUNCA uses el alias de columna en GROUP BY. "
    "Repite la expresión completa. Ejemplo correcto:\n"
    "  SELECT EXTRACT(YEAR FROM fecha) AS año, SUM(total) FROM ventas GROUP BY EXTRACT(YEAR FROM fecha)\n"
    "Ejemplo INCORRECTO:\n"
    "  SELECT EXTRACT(YEAR FROM fecha) AS año, SUM(total) FROM ventas GROUP BY año\n\n"
    "Responde ÚNICAMENTE con el SQL corregido, sin explicaciones."
)


def _strip_sql(raw):
    sql = raw.strip()
    if sql.startswith("```"):
        m = re.search(r"```(?:sql)?\s*([\s\S]*?)```", sql)
        if m:
            sql = m.group(1).strip()
    return sql


def _es_select_valido(sql):
    upper = sql.strip().upper()
    return upper.startswith("SELECT") or upper.startswith("WITH")


_HANDLERS = [
    {
        "name": "sql",
        "fn": sql_handler,
        "weight": 0,
        "patterns": [r".*"],
    },
]


def _normalize(text):
    return text.lower().strip()


def match_handler(message):
    return sql_handler
