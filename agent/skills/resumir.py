from .base import BaseSkill
from .. import llm

class ResumirSkill(BaseSkill):
    id = "resumir"

    def __init__(self):
        self._triggers = ["resume", "resumen", "resúmen", "resumir", "sintetiza", "abrevia"]

    def match(self, message: str) -> bool:
        msg = message.lower().strip()
        return any(t in msg for t in self._triggers)

    def execute(self, message: str, history=None) -> str:
        if not history:
            return "No hay historial para resumir."
        texts = [m["content"] for m in history if m["role"] == "assistant"]
        if not texts:
            return "No hay respuestas previas para resumir."
        target = texts[-1]
        prompt = f"Resume el siguiente texto en 3 líneas máximo:\n\n{target}"
        result = llm.generate(prompt, max_tokens=150)
        return result or "No pude generar el resumen."
