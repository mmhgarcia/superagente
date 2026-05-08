import re
import math
from .base import BaseSkill

SAFE_GLOBALS = {
    "abs": abs, "round": round, "min": min, "max": max,
    "sum": sum, "pow": pow, "int": int, "float": float,
    "math": math,
}

class CalcularSkill(BaseSkill):
    id = "calcular"

    def __init__(self):
        self._patterns = [
            r"cu[áa]nto es (\d+[\.\d]*\s*[\+\-\*\/\%]\s*\d+[\.\d]*)",
            r"(\d+[\.\d]*\s*[\+\-\*\/\%]\s*\d+[\.\d]*)",
            r"cu[áa]nto (?:es|da) ",
            r"calcula ",
            r"suma ",
            r"r[eé]stale? ",
            r"multiplica ",
            r"divide ",
            r"(\d+)\s*por\s*ciento\s*de\s*(\d+)",
        ]

    def match(self, message: str) -> bool:
        msg = message.lower().strip()
        return any(re.search(p, msg) for p in self._patterns)

    def execute(self, message: str, history=None) -> str:
        msg = message.lower().strip()

        m = re.search(r"(\d+)\s*(?:por\s*ciento|%)\s*de\s*(\d+)", msg)
        if m:
            pct = float(m.group(1))
            total = float(m.group(2))
            result = total * pct / 100
            return f"{pct:.0f}% de {total:.0f} = {result:.2f}"

        m = re.search(r"(\d+[\.\d]*\s*[\+\-\*\/\%]\s*\d+[\.\d]*)", msg)
        if m:
            expr = m.group(1).replace(" ", "")
            allowed = set("0123456789.+-*/%()")
            if not all(c in allowed for c in expr):
                return "Expresión no válida"
            try:
                result = eval(expr, {"__builtins__": {}}, SAFE_GLOBALS)
                return f"{expr} = {result}"
            except Exception:
                return "No pude realizar el cálculo"

        return "No pude interpretar la operación matemática"
