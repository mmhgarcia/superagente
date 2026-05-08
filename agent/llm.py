import requests

LM_STUDIO_URL = "http://host.docker.internal:1234/v1"
DEFAULT_MODEL = "tinyllama-1.1b-chat-v1.0"

def generate(prompt, system_prompt="", model=DEFAULT_MODEL, max_tokens=300, temperature=0.7):
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    try:
        resp = requests.post(f"{LM_STUDIO_URL}/chat/completions", json=payload, timeout=60)
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
