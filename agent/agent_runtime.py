import json
import os
import uuid
from .skill_store import SkillStore
from . import llm
from .skills.resumir import ResumirSkill

AGENTS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "agents.json")

_EXECUTABLE_SKILLS = {
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

    def ask(self, agent_id, message):
        agent = self._agents.get(agent_id)
        if not agent:
            return None, "Agente no encontrado"

        agent.history.append({"role": "user", "content": message})

        # Router de skills: probar skills ejecutables primero
        for sid in agent.skills:
            skill = _EXECUTABLE_SKILLS.get(sid)
            if skill and skill.match(message):
                result = skill.execute(message, history=agent.history)
                agent.history.append({"role": "assistant", "content": result})
                self._save()
                return agent.history, result

        # Fallback: responder con LLM
        skills_desc = []
        for sid in agent.skills:
            s = self._skill_store.get_skill(sid)
            if s:
                skills_desc.append(f"- {s['name']}: {s['description']}")
        skills_text = "\n".join(skills_desc)

        system_prompt = (
            f"Eres '{agent.name}', un agente autónomo.\n"
            f"Propósito: {agent.description}\n\n"
            f"Tus habilidades:\n{skills_text}\n\n"
            f"Responde de forma clara y útil."
        )

        history_text = "\n".join(
            f"{'Usuario' if m['role']=='user' else agent.name}: {m['content']}"
            for m in agent.history[-6:]
        )
        prompt = f"{history_text}\n{agent.name}:"

        response = llm.generate(prompt, system_prompt=system_prompt)

        if response is None:
            agent.history.pop()
            return None, "El LLM no respondió a tiempo"

        agent.history.append({"role": "assistant", "content": response})
        self._save()
        return agent.history, response
