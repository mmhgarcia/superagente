from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agent import create_agent as _create_agent
from agent import skill_store, runtime

app = FastAPI(title="Smart Factory de Agentes")

# --- Request models ---

class AgentRequest(BaseModel):
    name: str
    description: str

class AskRequest(BaseModel):
    message: str

class SkillRequest(BaseModel):
    id: str
    name: str
    description: str
    prompt_hint: str = ""

class CreateAgentRequest(BaseModel):
    name: str
    description: str
    skills: list[str] = ["base_chat"]

# --- Endpoints (Fase 1 backward compat) ---

@app.post("/generate_agent/")
async def generate_agent(req: AgentRequest):
    agent = _create_agent(req.name, req.description)
    return {"agent": agent}

# --- Endpoints Skills ---

@app.get("/skills")
async def list_skills():
    return {"skills": skill_store.list_skills()}

@app.post("/skills")
async def add_skill(req: SkillRequest):
    try:
        skill = skill_store.add_skill(req.id, req.name, req.description, req.prompt_hint)
        return {"skill": skill}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

class SkillUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    prompt_hint: str | None = None

@app.put("/skills/{skill_id}")
async def update_skill(skill_id: str, req: SkillUpdate):
    try:
        skill = skill_store.update_skill(skill_id, req.name, req.description, req.prompt_hint)
        return {"skill": skill}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.delete("/skills/{skill_id}")
async def delete_skill(skill_id: str):
    try:
        skill_store.remove_skill(skill_id)
        return {"status": "deleted"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# --- Endpoints Agentes ---

@app.post("/agents/create")
async def create_agent(req: CreateAgentRequest):
    agent = runtime.create_agent(req.name, req.description, req.skills)
    return {"agent": agent.to_dict()}

@app.get("/agents")
async def list_agents():
    return {"agents": [a.to_dict() for a in runtime.list_agents()]}

@app.get("/agents/{agent_id}")
async def get_agent(agent_id: str):
    agent = runtime.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agente no encontrado")
    return {"agent": agent.to_dict()}

@app.delete("/agents/{agent_id}")
async def delete_agent(agent_id: str):
    try:
        runtime.delete_agent(agent_id)
        return {"status": "deleted"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# --- Endpoints Chat ---

@app.post("/agents/{agent_id}/ask")
async def ask_agent(agent_id: str, req: AskRequest):
    history, response = runtime.ask(agent_id, req.message)
    if history is None:
        raise HTTPException(status_code=503, detail=response)
    return {"response": response, "history": history[-10:]}

@app.get("/agents/{agent_id}/history")
async def get_history(agent_id: str):
    agent = runtime.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agente no encontrado")
    return {"history": agent.history}
