import json
import os
import uuid
from .skill_store import SkillStore
from . import llm
from .parser import parse_response
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

    def _build_tools_text(self, agent):
        lines = []
        for sid in agent.skills:
            if sid in _EXECUTABLE_SKILLS:
                s = self._skill_store.get_skill(sid)
                if s:
                    schema = {
                        "calcular": 'Args: {"query": "expresión en lenguaje natural ej: 15% de 3400"}',
                        "resumir": 'Args: {"texto": "texto a resumir"}',
                        "consultar_db": (
                            'Args: {"query": "consulta SQL"}\n'
                            "  Tablas disponibles:\n"
                            "  - productos(id, nombre, categoria, precio, stock)\n"
                            "  - ventas(id, producto_id, cantidad, total, fecha, mes)\n"
                            "  Para resúmenes usa GROUP BY y funciones SUM/COUNT/AVG."
                        ),
                        "consultar_rag": 'Args: {"query": "texto de la consulta"}',
                    }.get(sid, "")
                    lines.append(f"- {sid}: {s['description']}\n  {schema}")
        if agent.name == "coordinador":
            lines.append('- delegar: pasar una tarea a otro agente. Args: {"agente": "nombre", "mensaje": "consulta"}')
        return "\n".join(lines)

    def _system_prompt(self, agent):
        tools_text = self._build_tools_text(agent)
        is_coordinador = agent.name == "coordinador"
        extra = ""
        if is_coordinador:
            agents_list = "\n".join(
                f"- {a.name}: {a.description}"
                for a in self._agents.values()
                if a.id != agent.id
            )
            extra = (
                f"\n\n"
                f"Para delegar tareas usa: {{\"tool\": \"delegar\", \"args\": {{\"agente\": \"nombre\", \"mensaje\": \"consulta\"}}}}\n"
                f"Agentes disponibles:\n{agents_list}"
            )
        has_tools = bool(tools_text.strip())
        base_rules = ""
        if has_tools:
            base_rules += (
                f"- Revisa si puedes responder usando una herramienta disponible. Si sí, USA la herramienta.\n"
                f"- Si la herramienta responde con datos, presenta esos datos como respuesta.\n"
                f"- No digas 'no disponible' sin antes intentar usar una herramienta.\n"
            )
        if "consultar_db" in (agent.skills or []):
            base_rules += (
                f"- IMPORTANTE: Para cualquier consulta sobre productos, ventas, stock o base de datos, DEBES usar consultar_db.\n"
                f"- NUNCA respondas con datos inventados o de tu conocimiento. Siempre consulta la base de datos primero.\n"
            )
        base_rules += (
            f"- Si no tienes la información ni herramientas para obtenerla, di honestamente que no está disponible\n"
            f"- Responde ÚNICAMENTE con JSON, sin texto adicional"
        )
        if is_coordinador:
            rules = (
                f"- Saluda/despídete directamente si es solo cortesía (hola, gracias, chao)\n"
                f"- Para TODO lo demás, DEBES usar delegar. NUNCA respondas preguntas técnicas directamente.\n"
                f"- Lee bien la descripción de cada agente antes de delegar\n"
                f"- Ejemplo: productos, stock, ventas o inventario → delegar a datos\n"
                f"- Ejemplo: horarios, facturas o políticas → delegar a atencion\n"
                f"- Ejemplo: cálculos, IVA o finanzas → delegar a finanzas\n"
                f"- Si un agente puede responder, USA delegar. No digas 'no disponible' sin antes delegar.\n"
                f"- Solo si ningún agente es adecuado, responde que no está disponible.\n"
                f"- Responde ÚNICAMENTE con JSON, sin texto adicional"
            )
        else:
            rules = base_rules
        return (
            f"Eres {agent.name}, un agente autónomo.\n\n"
            f"Propósito: {agent.description}\n\n"
            f"Responde ÚNICAMENTE en JSON. Elige entre:\n"
            f'  {{\"tool\": "nombre", "args": {{...}}}}  — si necesitas una herramienta\n'
            f'  {{\"reply": "tu respuesta aquí"}}        — si ya tienes la respuesta\n\n'
            f"Herramientas disponibles:\n{tools_text}"
            f"{extra}\n\n"
            f"Reglas:\n{rules}"
        )

    def _format_history(self, history):
        labels = {"user": "Usuario", "assistant": "Asistente", "system": "Sistema"}
        return "\n".join(
            f"{labels.get(m['role'], 'Sistema')}: {m['content']}"
            for m in history[-8:]
        )

    def _execute_tool(self, parsed):
        if parsed["name"] == "delegar":
            args = parsed["args"]
            target_name = args.get("agente", "")
            mensaje = args.get("mensaje", "")
            target = self._find_agent_by_name(target_name)
            if not target:
                return f"Error: agente '{target_name}' no encontrado"
            _, respuesta = self.ask(target.id, mensaje)
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

    def ask(self, agent_id, message):
        agent = self._agents.get(agent_id)
        if not agent:
            return None, "Agente no encontrado"

        agent.history.append({"role": "user", "content": message})

        if agent.name == "coordinador":
            routed = self._route_message(message)
            if routed:
                delegar = {"name": "delegar", "args": {"agente": routed, "mensaje": message}}
                result = self._execute_tool(delegar)
                agent.history.append({"role": "assistant", "content": str(result)})
                self._save()
                return agent.history, str(result)

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
