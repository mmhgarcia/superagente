from fastapi import FastAPI
from routes.skills import router as skills_router
from routes.agents import router as agents_router
from routes.health import router as health_router
from routes.config import router as config_router

from agent import llm

app = FastAPI(title="Smart Factory de Agentes")
app.include_router(skills_router)
app.include_router(agents_router)
app.include_router(health_router)
app.include_router(config_router)


@app.on_event("startup")
async def _load_config():
    llm.load_config()
