import json
import re

def parse_response(raw: str) -> dict:
    if not raw:
        return {"type": "error", "detail": "respuesta vacía"}

    text = raw.strip()

    if text.startswith("```"):
        m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        if m:
            text = m.group(1).strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"\{[^{}]*\}", text)
        if m:
            try:
                data = json.loads(m.group(0))
            except json.JSONDecodeError:
                return {"type": "error", "detail": "JSON inválido"}
        else:
            return {"type": "error", "detail": "no se encontró JSON"}

    if not isinstance(data, dict):
        return {"type": "error", "detail": "JSON no es un objeto"}

    if "reply" in data:
        return {"type": "reply", "content": data["reply"]}

    if "tool" in data:
        return {
            "type": "tool",
            "name": data["tool"],
            "args": data.get("args", {}),
        }

    return {"type": "error", "detail": "JSON sin reply ni tool"}
