import pytest
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agent.skill_store import SkillStore
from agent.agent_runtime import AgentRuntime

@pytest.fixture
def runtime():
    s = SkillStore()
    r = AgentRuntime(s)
    # limpiar agentes previos
    for a in r.list_agents():
        r.delete_agent(a.id)
    return r

def test_create_agent(runtime):
    agent = runtime.create_agent("test", "un agente de prueba")
    assert agent.name == "test"
    assert agent.description == "un agente de prueba"
    assert agent.skills == ["base_chat"]
    assert agent.id is not None

def test_create_agent_with_skills(runtime):
    agent = runtime.create_agent("test", "otro", skills=["base_chat", "calcular"])
    assert "calcular" in agent.skills

def test_list_agents(runtime):
    runtime.create_agent("a1", "desc1")
    runtime.create_agent("a2", "desc2")
    assert len(runtime.list_agents()) == 2

def test_get_agent(runtime):
    a = runtime.create_agent("get_test", "test")
    found = runtime.get_agent(a.id)
    assert found is not None
    assert found.name == "get_test"

def test_get_agent_not_found(runtime):
    assert runtime.get_agent("no_existe") is None

def test_delete_agent(runtime):
    a = runtime.create_agent("del_test", "test")
    runtime.delete_agent(a.id)
    assert runtime.get_agent(a.id) is None

def test_delete_nonexistent(runtime):
    with pytest.raises(ValueError):
        runtime.delete_agent("no_existe")

def test_ask_nonexistent_agent(runtime):
    history, err = runtime.ask("no_existe", "hola")
    assert history is None
    assert "no encontrado" in err
