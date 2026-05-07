import requests
import json

LM_STUDIO_URL = "http://host.docker.internal:1234/v1"
MODEL = "tinyllama-1.1b-chat-v1.0"

def create_agent(name: str, description: str) -> dict:
    prompt = f"Create an autonomous agent named {name} that {description}. Answer directly without reasoning."
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 300
    }
    try:
        resp = requests.post(f"{LM_STUDIO_URL}/chat/completions", json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        msg = data["choices"][0]["message"]
        content = msg.get("content", "").strip()
        if not content:
            content = msg.get("reasoning_content", "").strip()
        return {"name": name, "description": description, "status": "created", "response": content or "sin respuesta"}
    except requests.exceptions.ReadTimeout:
        return {"name": name, "description": description, "status": "timeout", "response": "LM Studio no respondió a tiempo"}
    except requests.exceptions.ConnectionError:
        return {"name": name, "description": description, "status": "warning", "response": "LM Studio no disponible en host"}
    except Exception as e:
        return {"name": name, "description": description, "status": "error", "response": str(e)[:100]}
