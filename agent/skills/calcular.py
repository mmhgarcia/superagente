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
        NUM = r"\d+(?:\.\d+)?"
        OPS = r"[\+\-\*\/\%]"
        CHAIN = rf"{NUM}(?:\s*{OPS}\s*{NUM})+"
        self._patterns = [
            rf"cu[áa]nto es ({CHAIN})",
            rf"({CHAIN})",
            r"cu[áa]nto (?:es|da) ",
            r"calcula ",
            r"suma ",
            r"r[eé]stale? ",
            r"multiplica ",
            r"divide ",
            r"(\d+)\s*por\s*ciento\s*de\s*(\d+)",
            r"ra[ií]z\s*(?:cuadrada|c[uú]bica)?\s*de\s*(\d+)",
            r"ra[ií]z\s*(?:cuadrada|c[uú]bica)?\s*\((\d+)\)",
            r"(seno|sen|sin|coseno|cos|tangente|tan)\s*de\s*(\d+)",
            r"(seno|sen|sin|coseno|cos|tangente|tan)\s*\((\d+)\)",
        ]

    def match(self, message: str) -> bool:
        msg = message.lower().strip()
        return any(re.search(p, msg) for p in self._patterns)

    def execute(self, message: str, history=None) -> str:
        msg = message.lower().strip()

        m = re.search(r"ra[ií]z\s*(cuadrada|c[uú]bica)?\s*(?:de\s*)?(\d+)", msg)
        if m:
            n = float(m.group(2))
            if m.group(1) and "cub" in m.group(1):
                result = n ** (1/3)
                rounded = round(result)
                display = rounded if abs(result - rounded) < 1e-10 else result
                return f"Raíz cúbica de {n:.0f} = {display}"
            else:
                result = math.sqrt(n)
                return f"Raíz cuadrada de {n:.0f} = {result}"

        m = re.search(r"(seno|sen|sin|coseno|cos|tangente|tan)\s*(?:de\s*)?\(?(\d+)\)?", msg)
        if m:
            raw_func = m.group(1)
            n = float(m.group(2))
            rad = math.radians(n)
            func_key = "sin" if raw_func in ("seno", "sen", "sin") else ("cos" if raw_func in ("coseno", "cos") else "tan")
            if func_key == "sin":
                result = math.sin(rad)
            elif func_key == "cos":
                result = math.cos(rad)
            else:
                result = math.tan(rad)
            label = {"sin": "Seno", "cos": "Coseno", "tan": "Tangente"}[func_key]
            return f"{label} de {n:.0f}° = {result:.4f}"

        m = re.search(r"(\d+)\s*(?:por\s*ciento|%)\s*de\s*(\d+)", msg)
        if m:
            pct = float(m.group(1))
            total = float(m.group(2))
            result = total * pct / 100
            return f"{pct:.0f}% de {total:.0f} = {result:.2f}"

        NUM = r"\d+(?:\.\d+)?"
        OPS = r"[\+\-\*\/\%]"
        m = re.search(rf"({NUM}(?:\s*{OPS}\s*{NUM})+)", msg)
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
