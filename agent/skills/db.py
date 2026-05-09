import sqlite3
import os
from .base import BaseSkill

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "demo.db")

class ConsultarDbSkill(BaseSkill):
    id = "consultar_db"

    def match(self, message: str) -> bool:
        triggers = ["base de datos", "consulta", "sql", "db", "datos", "producto", "venta", "stock"]
        return any(t in message.lower() for t in triggers)

    def execute(self, message: str, history=None) -> str:
        return "Usa la herramienta consultar_db con una consulta SQL."

    def execute_tool(self, args: dict) -> str:
        query = args.get("query", "")
        if not query:
            return "Error: se requiere una consulta SQL en el argumento 'query'."
        forbidden = ["drop", "delete", "insert", "update", "alter", "create", "truncate", "pragma", "replace", "attach", "detach", "reindex", "rename", "vacuum", "execute", "load_extension", "import"]
        q_lower = query.lower()
        for word in forbidden:
            if word in q_lower.split():
                return "Error: solo se permiten consultas SELECT."
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute(query)
            rows = c.fetchall()
            conn.close()
            if not rows:
                return "La consulta no devolvió resultados."
            col_names = [d[0] for d in c.description]
            header = " | ".join(col_names)
            separator = "-" * len(header)
            lines = [header, separator]
            for row in rows[:20]:
                vals = [str(v) if v is not None else "NULL" for v in row]
                lines.append(" | ".join(vals))
            if len(rows) > 20:
                lines.append(f"... y {len(rows) - 20} filas más")
            return "\n".join(lines)
        except Exception as e:
            return f"Error ejecutando consulta: {e}"
