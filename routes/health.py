from fastapi import APIRouter
import requests

router = APIRouter(prefix="", tags=["health"])

OLLAMA_URL = "http://host.docker.internal:11435"

@router.get("/health/llm")
async def health_llm():
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        if r.status_code == 200:
            models = [m["name"] for m in r.json().get("models", [])]
            return {"status": "ok", "models": models}
        return {"status": "error", "detail": f"HTTP {r.status_code}"}
    except requests.exceptions.ConnectionError:
        return {"status": "down", "detail": "Forwarder caído. Ejecuta: python3 scripts/ollama_forward.py"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
