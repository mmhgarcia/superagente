import json
import os
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="", tags=["config"])

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "config.json")

DEFAULT_CONFIG = {
    "model": "qwen2.5-coder:7b",
    "max_tokens": 4096,
    "temperature": 0.7,
}


def _load():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            return json.load(f)
    return dict(DEFAULT_CONFIG)


def _save(data):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


class ConfigUpdate(BaseModel):
    model: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None


@router.get("/config")
async def get_config():
    return _load()


@router.put("/config")
async def update_config(req: ConfigUpdate):
    cfg = _load()
    if req.model is not None:
        cfg["model"] = req.model
    if req.max_tokens is not None:
        cfg["max_tokens"] = req.max_tokens
    if req.temperature is not None:
        cfg["temperature"] = req.temperature
    _save(cfg)
    return cfg
