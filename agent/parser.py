import json
import re

def _find_json_objects(text):
    objs = []
    i = 0
    while i < len(text):
        if text[i] == "{":
            depth = 0
            j = i
            while j < len(text):
                if text[j] == "{":
                    depth += 1
                elif text[j] == "}":
                    depth -= 1
                    if depth == 0:
                        objs.append(text[i : j + 1])
                        i = j
                        break
                elif text[j] == '"':
                    j += 1
                    while j < len(text) and text[j] != '"':
                        if text[j] == "\\":
                            j += 1
                        j += 1
                j += 1
        i += 1
    return objs


def parse_response(raw):
    if not raw:
        return {"type": "error", "detail": "respuesta vacía"}

    text = raw.strip()

    if text.startswith("```"):
        m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        if m:
            text = m.group(1).strip()

    candidates = _find_json_objects(text)

    for cand in candidates:
        try:
            data = json.loads(cand)
        except json.JSONDecodeError:
            continue
        if not isinstance(data, dict):
            continue
        if "tool" in data:
            return {
                "type": "tool",
                "name": data["tool"],
                "args": data.get("args", {}),
            }
        if "reply" in data:
            return {"type": "reply", "content": data["reply"]}

    try:
        data = json.loads(text)
        if isinstance(data, dict):
            if "tool" in data:
                return {"type": "tool", "name": data["tool"], "args": data.get("args", {})}
            if "reply" in data:
                return {"type": "reply", "content": data["reply"]}
    except json.JSONDecodeError:
        pass

    for cand in candidates:
        try:
            data = json.loads(cand)
            if isinstance(data, dict):
                if "tool" in data:
                    return {"type": "tool", "name": data["tool"], "args": data.get("args", {})}
                if "reply" in data:
                    return {"type": "reply", "content": data["reply"]}
        except json.JSONDecodeError:
            continue

    return {"type": "error", "detail": "no se encontró JSON válido con tool o reply"}
