import os
import re
import psycopg2

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
        return str(e)
    finally:
        cur.close()
        conn.close()


SCHEMA = (
    "Genera SQL para PostgreSQL.\n\n"
    "Tablas:\n"
    "  productos(id, nombre, categoria, precio, stock, stock_minimo)\n"
    "  ventas(id, producto_id, cantidad, total, fecha, mes)\n\n"
    "Funciones PostgreSQL: SUM, COUNT, AVG, MIN, MAX, EXTRACT, TO_CHAR, ROUND\n"
    "  - ROUND(valor::numeric, 2) para redondear con decimales. Ej: ROUND((SUM(total)/3.0)::numeric, 2)\n"
    "  - EXTRACT(YEAR FROM fecha) para año\n"
    "  - EXTRACT(MONTH FROM fecha) para mes\n"
    "  - EXTRACT(QUARTER FROM fecha) para trimestre (devuelve 1, 2, 3, 4)\n"
    "  - CASE WHEN EXTRACT(MONTH FROM fecha) <= 6 THEN 1 ELSE 2 END para semestre (H1/H2)\n"
    "  - TO_CHAR(fecha, 'YYYY-MM-DD') para formatear fechas\n"
    "  - NO USES: strftime(), DATE_FORMAT(), YEAR(), MONTH()\n\n"
    "Reglas:\n"
    "- Solo SELECT (nunca INSERT, UPDATE, DELETE, DROP, ALTER)\n"
    "- Si usas EXTRACT() o cualquier expresión en SELECT, repite la expresión completa en GROUP BY, no uses el alias.\n"
    "  Ejemplo correcto: SELECT EXTRACT(YEAR FROM fecha) AS año, SUM(total) FROM ventas GROUP BY EXTRACT(YEAR FROM fecha)\n"
    "  Ejemplo INCORRECTO: ... GROUP BY año\n"
    "- Cuando pidan solo 'año' o 'por año': agrupa ÚNICAMENTE por EXTRACT(YEAR FROM fecha), sin mes ni trimestre.\n"
    "- Cuando pidan 'trimestre' o 'trimestral': agrupa usando EXTRACT(QUARTER FROM fecha).\n"
    "- Cuando pidan 'semestre': usa CASE WHEN EXTRACT(MONTH FROM fecha) <= 6 THEN 1 ELSE 2 END.\n"
    "- Si piden agrupar (por categoria, por mes), usa GROUP BY\n"
    "- Proyecciones (cuando pidan 'proyectar', 'proyección', 'pronóstico', 'estimación'):\n"
    "  - Calcula el promedio mensual del período de referencia: SUM(total) / N_meses\n"
    "  - Multiplica por los meses del período objetivo para obtener la proyección\n"
    "  - Usa WITH (CTE) para separar la referencia de la proyección final\n"
    "  - Ejemplo: proyectar ventas Q1 2026 basado en Q4 2025:\n"
    "    WITH ref AS (\n"
    "      SELECT SUM(total) / 3.0 AS monthly_avg\n"
    "      FROM ventas\n"
    "      WHERE EXTRACT(YEAR FROM fecha) = 2025 AND EXTRACT(QUARTER FROM fecha) = 4\n"
    "    )\n"
    "    SELECT 'Q1 2026' AS periodo, ROUND((monthly_avg * 3)::numeric, 2) AS proyeccion FROM ref\n"
    "- Responde ÚNICAMENTE con SQL, sin explicaciones ni formato"
)


def sql_handler(message):
    from .llm import generate
    raw = generate(message, system_prompt=SCHEMA)
    if not raw:
        return "El LLM no respondió."
    sql = raw.strip()
    if sql.startswith("```"):
        m = re.search(r"```(?:sql)?\s*([\s\S]*?)```", sql)
        if m:
            sql = m.group(1).strip()
    sql_upper = sql.strip().upper()
    if not sql_upper.startswith("SELECT") and not sql_upper.startswith("WITH"):
        return f"SQL no válido (solo SELECT): {sql[:100]}"
    error = _validate_sql(sql)
    if error:
        return f"SQL inválido: {error}"
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
