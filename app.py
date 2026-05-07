from fastapi import FastAPI
from pydantic import BaseModel
from agent import create_agent

app = FastAPI()

class AgentRequest(BaseModel):
    name: str
    description: str

@app.post("/generate_agent/")
async def generate_agent(req: AgentRequest):
    agent = create_agent(req.name, req.description)
    return {"agent": agent}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
