from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from agent import skill_store

router = APIRouter(prefix="", tags=["skills"])

class SkillRequest(BaseModel):
    id: str
    name: str
    description: str
    prompt_hint: str = ""

class SkillUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    prompt_hint: Optional[str] = None


@router.get("/skills")
async def list_skills():
    return {"skills": skill_store.list_skills()}

@router.post("/skills")
async def add_skill(req: SkillRequest):
    try:
        skill = skill_store.add_skill(req.id, req.name, req.description, req.prompt_hint)
        return {"skill": skill}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/skills/{skill_id}")
async def update_skill(skill_id: str, req: SkillUpdate):
    try:
        skill = skill_store.update_skill(skill_id, req.name, req.description, req.prompt_hint)
        return {"skill": skill}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/skills/{skill_id}")
async def delete_skill(skill_id: str):
    try:
        skill_store.remove_skill(skill_id)
        return {"status": "deleted"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
