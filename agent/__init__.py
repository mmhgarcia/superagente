from .skill_store import SkillStore
from .agent_runtime import AgentRuntime

skill_store = SkillStore()
runtime = AgentRuntime(skill_store)

def create_agent(name: str, description: str) -> dict:
    agent = runtime.create_agent(name, description)
    return {
        "id": agent.id,
        "name": agent.name,
        "description": agent.description,
        "skills": agent.skills,
        "status": "created",
    }
