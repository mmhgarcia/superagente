import json
import os
from .base import BaseSkill

RAG_API_URL = os.getenv("RAG_API_URL", "")


class ConsultarRagSkill(BaseSkill):
    id = "consultar_rag"

    def match(self, message: str) -> bool:
        triggers = ["rag", "buscar", "investigar", "documento", "informe", "manual", "consulta", "pdf", "archivo"]
        return any(t in message.lower() for t in triggers)

    def execute(self, message: str, history=None) -> str:
        if not RAG_API_URL:
            return "El servicio RAG no está configurado. Define la variable RAG_API_URL."
        try:
            import httpx
            resp = httpx.post(
                f"{RAG_API_URL}/query",
                json={"query": message, "top_k": 5},
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("answer", json.dumps(data, indent=2, ensure_ascii=False))
        except ImportError:
            return "Error: httpx no está instalado (pip install httpx)"
        except Exception as e:
            return f"Error consultando RAG: {e}"

    def execute_tool(self, args: dict) -> str:
        query = args.get("query") or args.get("texto") or args.get("consulta") or ""
        return self.execute(query)
