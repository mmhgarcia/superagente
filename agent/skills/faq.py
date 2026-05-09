import json
import os
from .base import BaseSkill

FAQ_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "faq.json")

class ConsultarFaqSkill(BaseSkill):
    id = "consultar_faq"

    def __init__(self):
        self._faqs = self._load_faqs()

    def _load_faqs(self):
        if not os.path.exists(FAQ_PATH):
            return []
        with open(FAQ_PATH) as f:
            return json.load(f)

    def match(self, message: str) -> bool:
        msg = message.lower().strip()
        for faq in self._faqs:
            if any(k in msg for k in faq["keywords"]):
                return True
        return False

    def execute(self, message: str, history=None) -> str:
        msg = message.lower().strip()
        best = None
        best_score = 0
        for faq in self._faqs:
            score = sum(1 for k in faq["keywords"] if k in msg)
            if score > best_score:
                best_score = score
                best = faq
        if best:
            return f"{best['question']}\n\n{best['answer']}"
        return "No tengo información sobre esa pregunta."

    def execute_tool(self, args: dict) -> str:
        query = args.get("query", "")
        return self.execute(query)
