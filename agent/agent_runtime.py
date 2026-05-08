import json
import os
import uuid
from .skill_store import SkillStore
from . import llm
from .parser import parse_response
from .skills.calcular import CalcularSkill
from .skills.resumir import ResumirSkill

AGENTS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "agents.json")

_EXECUTABLE_SKILLS = {
    "calcular": CalcularSkill(),
    "resumir": ResumirSkill(),
}


class Agent:
    def __init__(self, agent_id, name, description, skills=None):
        self.id = agent_id
        self.name = name
        self.description = description
        self.skills = skills or ["base_chat"]
        self.history = []

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "skills": self.skills,
            "history": self.history[-10:],
        }


class AgentRuntime:
    def __init__(self, skill_store: SkillStore):
        self._agents = {}
        self._skill_store = skill_store
        self._load()

    def _load(self):
        if os.path.exists(AGENTS_PATH):
            with open(AGENTS_PATH) as f:
                data = json.load(f)
            for a in data:
                agent = Agent(a["id"], a["name"], a["description"], a.get("skills", ["base_chat"]))
                agent.history = a.get("history", [])
                self._agents[agent.id] = agent

    def _save(self):
        os.makedirs(os.path.dirname(AGENTS_PATH), exist_ok=True)
        with open(AGENTS_PATH, "w") as f:
            json.dump([a.to_dict() for a in self._agents.values()], f, indent=2, ensure_ascii=False)

    def create_agent(self, name, description, skills=None):
        agent_id = str(uuid.uuid4())[:8]
        agent = Agent(agent_id, name, description, skills or ["base_chat"])
        self._agents[agent_id] = agent
        self._save()
        return agent

    def get_agent(self, agent_id):
        return self._agents.get(agent_id)

    def list_agents(self):
        return list(self._agents.values())

    def delete_agent(self, agent_id):
        if agent_id not in self._agents:
            raise ValueError(f"Agente '{agent_id}' no encontrado")
        del self._agents[agent_id]
        self._save()

    def _build_tools_text(self, agent):
        lines = []
        for sid in agent.skills:
            if sid in _EXECUTABLE_SKILLS:
                s = self._skill_store.get_skill(sid)
                if s:
                    schema = {
                        "calcular": 'Args: {"query": "expresión en lenguaje natural ej: 15% de 3400"}',
                        "resumir": 'Args: {"texto": "texto a resumir"}',
                    }.get(sid, "")
                    lines.append(f"- {sid}: {s['description']} {schema}")
        return "\n".join(lines)

    def _system_prompt(self, agent):
        tools_text = self._build_tools_text(agent)
        return (
            f"Eres {agent.name}, un agente autónomo con acceso a herramientas.\n\n"
            f"Propósito: {agent.description}\n\n"
            f"Responde ÚNICAMENTE en JSON. El JSON debe tener esta estructura:\n\n"
            f"1. Si necesitas usar una herramienta:\n"
            f'   {{"tool": "nombre", "args": {{...}}}}\n\n'
            f"2. Si ya tienes la respuesta:\n"
            f'   {{"reply": "tu respuesta aquí"}}\n\n'
            f"Herramientas disponibles:\n{tools_text}\n\n"
            f"Reglas:\n"
            f"- Un solo tool o reply por respuesta\n"
            f"- Nunca mezcles tool con reply\n"
            f"- No agregues texto fuera del JSON"
        )

    def _format_history(self, history):
        labels = {"user": "Usuario", "assistant": "Asistente", "system": "Sistema"}
        return "\n".join(
            f"{labels.get(m['role'], 'Sistema')}: {m['content']}"
            for m in history[-8:]
        )

    def _execute_tool(self, parsed):
        skill = _EXECUTABLE_SKILLS.get(parsed["name"])
        if not skill:
            return f"Error: herramienta '{parsed['name']}' no disponible"
        return skill.execute_tool(parsed["args"])

    def ask(self, agent_id, message):
        agent = self._agents.get(agent_id)
        if not agent:
            return None, "Agente no encontrado"

        agent.history.append({"role": "user", "content": message})
        system = self._system_prompt(agent)
        working = list(agent.history)
        final = None
        max_steps = 3

        for step in range(max_steps):
            history_text = self._format_history(working)
            prompt = f"{history_text}\nAsistente:"

            raw = llm.generate(prompt, system_prompt=system)
            if raw is None:
                if step == 0:
                    agent.history.pop()
                return None, "El LLM no respondió a tiempo"

            parsed = parse_response(raw)

            if parsed["type"] == "reply":
                final = parsed["content"]
                break
            elif parsed["type"] == "tool":
                result = self._execute_tool(parsed)
                working.append({"role": "assistant", "content": raw})
                working.append({"role": "system", "content": f"Resultado de {parsed['name']}: {result}"})
                final = result
            else:
                final = raw
                break

        if final is None:
            final = "El agente no pudo completar la solicitud"

        agent.history.append({"role": "assistant", "content": str(final)})
        self._save()
        return agent.history, str(final)
