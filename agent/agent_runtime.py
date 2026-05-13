import json
import os
import uuid
from .skill_store import SkillStore
from . import llm
from .parser import parse_response
from .handlers import sql_handler
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

    def _route_message(self, message):
        msg = message.lower()
        routes = {
            "datos": ["producto", "inventario", "stock", "precio", "venta", "categoria", "categoría", "listado", "cuántos", "cuantos", "registrado"],
            "atencion": ["horario", "factura", "devolucion", "devolución", "envio", "envío", "pago", "garantia", "garantía", "contacto", "política", "politica"],
            "finanzas": ["iva", "finanzas", "contabilidad", "impuesto", "presupuesto", "interés", "interes", "tasa", "descuento"],
        }
        for agent_name, keywords in routes.items():
            if any(k in msg for k in keywords):
                target = self._find_agent_by_name(agent_name)
                if target:
                    return agent_name
        return None

    @staticmethod
    def _es_conversacion(message):
        import re
        msg = message.lower().strip()
        saludos = ["hola", "buenos", "buen", "que tal", "como estas", "hey", "hello", "hi"]
        despedidas = ["chao", "adios", "nos vemos", "gracias", "bye", "hasta luego", "saludos"]
        apoyo = ["ok", "vale", "de acuerdo", "perfecto", "entiendo"]
        if any(s in msg for s in saludos + despedidas + apoyo):
            return True
        if re.search(r"^(si|no|ok|vale)\W*$", msg):
            return True
        return False

    def ask(self, agent_id, message):
        agent = self._agents.get(agent_id)
        if not agent:
            return None, "Agente no encontrado"

        agent.history.append({"role": "user", "content": message})

        if self._es_conversacion(message):
            system = "Eres un asistente amigable. Responde saludos de forma breve y natural."
            raw = llm.generate(message, system_prompt=system)
            final = raw or "Hola!"
            agent.history.append({"role": "assistant", "content": final})
            self._save()
            return agent.history, final, 100

        if agent.name == "coordinador":
            routed = self._route_message(message)
            if routed:
                delegar = {"name": "delegar", "args": {"agente": routed, "mensaje": message}}
                result = self._execute_tool(delegar)
                agent.history.append({"role": "assistant", "content": str(result)})
                self._save()
                return agent.history, str(result), 100

        result = sql_handler(message)
        agent.history.append({"role": "assistant", "content": str(result)})
        self._save()
        return agent.history, str(result), 100
