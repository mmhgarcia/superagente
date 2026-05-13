import json
import os
import requests

OLLAMA_URL = "http://host.docker.internal:11435/v1"

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "config.json")

_config = {
    "model": "qwen2.5-coder:7b",
    "max_tokens": 4096,
    "temperature": 0.7,
}


def load_config():
    global _config
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            data = json.load(f)
        _config.update(data)


def generate(prompt, system_prompt="", temperature=None):
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": _config["model"],
        "messages": messages,
        "temperature": _config["temperature"] if temperature is None else temperature,
        "max_tokens": _config["max_tokens"],
    }
    try:
        resp = requests.post(f"{OLLAMA_URL}/chat/completions", json=payload, timeout=300)
        resp.raise_for_status()
        data = resp.json()
        msg = data["choices"][0]["message"]
        content = msg.get("content", "").strip()
        if not content:
            content = msg.get("reasoning_content", "").strip()
        return content or "sin respuesta"
    except requests.exceptions.ReadTimeout:
        return None
    except requests.exceptions.ConnectionError:
        return None
