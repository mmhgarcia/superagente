import pytest
from agent.parser import parse_response

def test_reply_raw():
    r = parse_response('{"reply": "hola"}')
    assert r == {"type": "reply", "content": "hola"}

def test_reply_in_codeblock():
    r = parse_response('```json\n{"reply": "adios"}\n```')
    assert r == {"type": "reply", "content": "adios"}

def test_reply_codeblock_no_lang():
    r = parse_response('```\n{"reply": "ok"}\n```')
    assert r == {"type": "reply", "content": "ok"}

def test_tool_raw():
    r = parse_response('{"tool": "calcular", "args": {"query": "2+2"}}')
    assert r == {"type": "tool", "name": "calcular", "args": {"query": "2+2"}}

def test_tool_no_args():
    r = parse_response('{"tool": "resumir"}')
    assert r == {"type": "tool", "name": "resumir", "args": {}}

def test_extra_text_before_json():
    r = parse_response('Claro, aqui tienes:\n{"reply": "resultado"}')
    assert r == {"type": "reply", "content": "resultado"}

def test_invalid_json():
    r = parse_response('hola mundo')
    assert r["type"] == "error"

def test_empty():
    r = parse_response("")
    assert r["type"] == "error"

def test_no_reply_nor_tool():
    r = parse_response('{"foo": "bar"}')
    assert r["type"] == "error"
