from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from agent import create_agent as _create_agent
from agent import runtime

router = APIRouter(prefix="", tags=["agents"])

class AgentRequest(BaseModel):
    name: str
    description: str

class CreateAgentRequest(BaseModel):
    name: str
    description: str
    skills: list[str] = ["base_chat"]

class UpdateAgentRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    skills: Optional[list[str]] = None

class AskRequest(BaseModel):
    message: str


@router.post("/generate_agent/")
async def generate_agent(req: AgentRequest):
    agent = _create_agent(req.name, req.description)
    return {"agent": agent}

@router.post("/agents/create")
async def create_agent(req: CreateAgentRequest):
    agent = runtime.create_agent(req.name, req.description, req.skills)
    return {"agent": agent.to_dict()}

@router.get("/agents")
async def list_agents():
    return {"agents": [a.to_dict() for a in runtime.list_agents()]}

@router.get("/agents/{agent_id}")
async def get_agent(agent_id: str):
    agent = runtime.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agente no encontrado")
    return {"agent": agent.to_dict()}

@router.put("/agents/{agent_id}")
async def update_agent(agent_id: str, req: UpdateAgentRequest):
    try:
        agent = runtime.update_agent(agent_id, req.name, req.description, req.skills)
        return {"agent": agent.to_dict()}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/agents/{agent_id}")
async def delete_agent(agent_id: str):
    try:
        runtime.delete_agent(agent_id)
        return {"status": "deleted"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/agents/{agent_id}/ask")
async def ask_agent(agent_id: str, req: AskRequest):
    history, response = runtime.ask(agent_id, req.message)
    if history is None:
        raise HTTPException(status_code=503, detail=response)
    return {"response": response, "history": history[-10:]}

@router.get("/agents/{agent_id}/history")
async def get_history(agent_id: str):
    agent = runtime.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agente no encontrado")
    return {"history": agent.history}
