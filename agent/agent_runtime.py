import json
import os
import uuid
import psycopg2
from .skill_store import SkillStore
from . import llm
from .parser import parse_response
from .handlers import sql_handler, PG_DSN
from .intent import clasificar_intencion
from .skills.calcular import CalcularSkill
from .skills.resumir import ResumirSkill
from .skills.faq import ConsultarFaqSkill
from .skills.db import ConsultarDbSkill
from .skills.consultar_rag import ConsultarRagSkill

AGENTS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "agents.json")

_EXECUTABLE_SKILLS = {
    "calcular": CalcularSkill(),
    "resumir": ResumirSkill(),
    "consultar_faq": ConsultarFaqSkill(),
    "consultar_db": ConsultarDbSkill(),
    "consultar_rag": ConsultarRagSkill(),
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
        self._init_db()
        self._migrate_json()
        self._load()

    def _conn(self):
        return psycopg2.connect(PG_DSN)

    def _init_db(self):
        conn = self._conn()
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS agents (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                skills JSONB NOT NULL DEFAULT '["base_chat"]',
                history JSONB NOT NULL DEFAULT '[]'
            )
        """)
        cur.close()
        conn.close()

    def _migrate_json(self):
        if not os.path.exists(AGENTS_PATH):
            return
        with open(AGENTS_PATH) as f:
            data = json.load(f)
        if not data:
            return
        conn = self._conn()
        conn.autocommit = True
        cur = conn.cursor()
        for a in data:
            cur.execute(
                "INSERT INTO agents (id, name, description, skills, history) "
                "VALUES (%s, %s, %s, %s, %s) ON CONFLICT (id) DO NOTHING",
                (a["id"], a["name"], a.get("description", ""),
                 json.dumps(a.get("skills", ["base_chat"])),
                 json.dumps(a.get("history", []))),
            )
        cur.close()
        conn.close()
        os.remove(AGENTS_PATH)

    def _load(self):
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("SELECT id, name, description, skills, history FROM agents ORDER BY name")
        for row in cur.fetchall():
            agent = Agent(row[0], row[1], row[2], row[3])
            agent.history = row[4]
            self._agents[agent.id] = agent
        cur.close()
        conn.close()

    def _save(self):
        conn = self._conn()
        conn.autocommit = True
        cur = conn.cursor()
        for agent in self._agents.values():
            cur.execute(
                "INSERT INTO agents (id, name, description, skills, history) "
                "VALUES (%s, %s, %s, %s, %s) "
                "ON CONFLICT (id) DO UPDATE SET "
                "name=EXCLUDED.name, description=EXCLUDED.description, "
                "skills=EXCLUDED.skills, history=EXCLUDED.history",
                (agent.id, agent.name, agent.description,
                 json.dumps(agent.skills),
                 json.dumps(agent.history)),
            )
        cur.close()
        conn.close()

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
        conn = self._conn()
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("DELETE FROM agents WHERE id = %s", (agent_id,))
        cur.close()
        conn.close()

    def update_agent(self, agent_id, name=None, description=None, skills=None):
        agent = self._agents.get(agent_id)
        if not agent:
            raise ValueError(f"Agente '{agent_id}' no encontrado")
        if name is not None:
            agent.name = name
        if description is not None:
            agent.description = description
        if skills is not None:
            agent.skills = skills
        self._save()
        return agent

    def _execute_tool(self, parsed):
        if parsed["name"] == "delegar":
            args = parsed["args"]
            target_name = args.get("agente", "")
            mensaje = args.get("mensaje", "")
            target = self._find_agent_by_name(target_name)
            if not target:
                return f"Error: agente '{target_name}' no encontrado"
            _, respuesta, _ = self.ask(target.id, mensaje)
            return respuesta
        skill = _EXECUTABLE_SKILLS.get(parsed["name"])
        if not skill:
            return f"Error: herramienta '{parsed['name']}' no disponible"
        return skill.execute_tool(parsed["args"])

    def _find_agent_by_name(self, name):
        for a in self._agents.values():
            if a.name == name:
                return a
        return None

    def ask(self, agent_id, message):
        agent = self._agents.get(agent_id)
        if not agent:
            return None, "Agente no encontrado"

        agent.history.append({"role": "user", "content": message})

        intent = clasificar_intencion(message)

        if intent == "conversacion":
            system = "Eres un asistente amigable. Responde saludos de forma breve y natural."
            raw = llm.generate(message, system_prompt=system)
            final = raw or "Hola!"
            agent.history.append({"role": "assistant", "content": final})
            self._save()
            return agent.history, final, 100

        if agent.name == "coordinador" and intent in ("datos", "atencion", "finanzas"):
            target = self._find_agent_by_name(intent)
            if target:
                delegar = {"name": "delegar", "args": {"agente": intent, "mensaje": message}}
                result = self._execute_tool(delegar)
                agent.history.append({"role": "assistant", "content": str(result)})
                self._save()
                return agent.history, str(result), 100

        result = sql_handler(message)
        agent.history.append({"role": "assistant", "content": str(result)})
        self._save()
        return agent.history, str(result), 100
