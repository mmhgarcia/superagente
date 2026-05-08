import pytest
import tempfile
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agent.skill_store import SkillStore

@pytest.fixture
def store():
    prev_path = os.path.join(os.path.dirname(__file__), "..", "data")
    os.makedirs(prev_path, exist_ok=True)
    s = SkillStore()
    yield s

def test_list_skills(store):
    skills = store.list_skills()
    assert len(skills) >= 4
    ids = [s["id"] for s in skills]
    assert "base_chat" in ids
    assert "calcular" in ids

def test_get_skill(store):
    s = store.get_skill("base_chat")
    assert s is not None
    assert s["name"] == "Conversación básica"

def test_get_skill_not_found(store):
    s = store.get_skill("nonexistent")
    assert s is None

def test_add_skill(store):
    unique_id = f"test_{id(store)}"
    s = store.add_skill(unique_id, "Test", "Una skill de prueba")
    assert s["id"] == unique_id
    assert store.get_skill(unique_id) is not None
    store.remove_skill(unique_id)

def test_add_duplicate_skill(store):
    with pytest.raises(ValueError):
        store.add_skill("base_chat", "Duplicado", "Ya existe")

def test_remove_skill(store):
    unique_id = f"temp_{id(store)}"
    store.add_skill(unique_id, "Temp", "Temporal")
    store.remove_skill(unique_id)
    assert store.get_skill(unique_id) is None

def test_remove_nonexistent_skill(store):
    with pytest.raises(ValueError):
        store.remove_skill("no_existe")
