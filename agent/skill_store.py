import json
import os

STORE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "skills.json")

_default_skills = [
    {
        "id": "base_chat",
        "name": "Conversación básica",
        "description": "Mantener conversaciones fluidas en lenguaje natural.",
        "prompt_hint": "Eres un asistente conversacional. Responde de manera clara y útil."
    },
    {
        "id": "calcular",
        "name": "Operaciones matemáticas",
        "description": "Realizar cálculos aritméticos básicos (suma, resta, multiplicación, división).",
        "prompt_hint": "Cuando te pidan un cálculo, resuélvelo paso a paso."
    },
    {
        "id": "formatear",
        "name": "Formateo estructurado",
        "description": "Dar formato ordenado a las respuestas usando listas, tablas o código.",
        "prompt_hint": "Siempre que sea útil, estructura tu respuesta con listas, tablas o bloques de código."
    },
    {
        "id": "resumir",
        "name": "Resumir textos",
        "description": "Resumir información extensa en pocos párrafos.",
        "prompt_hint": "Cuando te pidan un resumen, extrae solo los puntos clave."
    },
]


class SkillStore:
    def __init__(self):
        self._skills = {}
        self._load()

    def _load(self):
        if os.path.exists(STORE_PATH):
            with open(STORE_PATH) as f:
                data = json.load(f)
            self._skills = {s["id"]: s for s in data}
        else:
            for s in _default_skills:
                self._skills[s["id"]] = s
            self._save()

    def _save(self):
        os.makedirs(os.path.dirname(STORE_PATH), exist_ok=True)
        with open(STORE_PATH, "w") as f:
            json.dump(list(self._skills.values()), f, indent=2, ensure_ascii=False)

    def list_skills(self):
        return list(self._skills.values())

    def get_skill(self, skill_id):
        return self._skills.get(skill_id)

    def add_skill(self, skill_id, name, description, prompt_hint=""):
        if skill_id in self._skills:
            raise ValueError(f"Skill '{skill_id}' ya existe")
        skill = {
            "id": skill_id,
            "name": name,
            "description": description,
            "prompt_hint": prompt_hint,
        }
        self._skills[skill_id] = skill
        self._save()
        return skill

    def update_skill(self, skill_id, name=None, description=None, prompt_hint=None):
        if skill_id not in self._skills:
            raise ValueError(f"Skill '{skill_id}' no encontrada")
        skill = self._skills[skill_id]
        if name is not None:
            skill["name"] = name
        if description is not None:
            skill["description"] = description
        if prompt_hint is not None:
            skill["prompt_hint"] = prompt_hint
        self._save()
        return skill

    def remove_skill(self, skill_id):
        if skill_id not in self._skills:
            raise ValueError(f"Skill '{skill_id}' no encontrada")
        del self._skills[skill_id]
        self._save()
