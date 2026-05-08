from fastapi import FastAPI
from routes.skills import router as skills_router
from routes.agents import router as agents_router
from routes.health import router as health_router

app = FastAPI(title="Smart Factory de Agentes")
app.include_router(skills_router)
app.include_router(agents_router)
app.include_router(health_router)
