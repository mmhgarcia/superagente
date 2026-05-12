# Plan: Superagente Agéntico

Partiendo desde lo más simple, sin tocar rag_project.

---

## Fase 1 — Coordinador con LLM (1 archivo, ~10 líneas)

**Qué**: Eliminar el bypass del coordinador. Hoy `_route_message()` decide con keywords qué agente llamar. Que lo decida el LLM.

**Dónde**: `agent/agent_runtime.py:223-230`

**Cambio**:
```python
# ANTES
if agent.name == "coordinador":
    routed = self._route_message(message)
    if routed:
        delegar = {"name": "delegar", "args": {"agente": routed, "mensaje": message}}
        result = self._execute_tool(delegar)
        agent.history.append(...)
        return ...

# DESPUÉS
# Simplemente borrar el bloque if. El coordinador cae en el loop LLM normal
# (línea 232 en adelante). Ya tiene el tool "delegar" en su system prompt.
```

El coordinador ya tiene en su system prompt:
- Lista de agentes disponibles con descripciones
- Tool `delegar` con formato `{"agente": "nombre", "mensaje": "consulta"}`
- Regla: "Para TODO lo demás, DEBES usar delegar"

Solo falta **dejarlo decidir al LLM** en vez de cortocircuitar con keywords.

**Riesgo**: Latencia. Hoy el ruteo es instantáneo. Con LLM serán 1-2 min por consulta. La ganancia es que el LLM entiende contexto y puede decidir mejor que un keyword match.

**Archivos a tocar**: 1 (`agent_runtime.py`)
**Líneas a cambiar**: ~10

---

## Fase 2 — Confidence desde el LLM (3 archivos)

**Qué**: Que el LLM incluya su nivel de confianza en la respuesta, en vez de valores hardcodeados.

**Dónde**: `agent/parser.py`, `agent/agent_runtime.py`, `routes/agents.py`

**Cambio en parser**:
```python
# parser.py — extraer confidence del JSON
{
    "reply": "...",
    "confidence": 85  # 0-100, lo decide el LLM
}
```

**Cambio en runtime**:
```python
# En lugar de:
#   confidence = 20/50/90/100
# Usar:
#   confidence = parsed.get("confidence", 50)
```

**Cambio en system prompt**:
```text
Responde en JSON. Incluye siempre "confidence" (0-100) según qué tan seguro
estás de tu respuesta basado en los datos que tienes.
Ejemplo: {"reply": "La respuesta es...", "confidence": 92}
```

**Archivos a tocar**: 3
**Líneas a cambiar**: ~15

---

## Fase 3 — Loop sin límite fijo (1 archivo)

**Qué**: Reemplazar `max_steps = 3` por un loop que termine cuando el LLM decida que ya tiene respuesta, no cuando se acaben los pasos.

**Dónde**: `agent/agent_runtime.py:236`

**Cambio**:
```python
# ANTES
max_steps = 3
for step in range(max_steps):
    ...
    if parsed["type"] == "reply":
        final = parsed["content"]
        break
    ...

# DESPUÉS
max_steps = 10  # safety bound más amplio
min_confidence = 70
for step in range(max_steps):
    ...
    if parsed["type"] == "reply":
        confidence = parsed.get("confidence", 50)
        if confidence >= min_confidence or step == max_steps - 1:
            final = parsed["content"]
            break
        else:
            # El LLM no está seguro, puede intentar de nuevo
            working.append({"role": "system", "content": f"Confianza baja ({confidence}). Si puedes, busca más información o reformula."})
            continue
    ...
```

**Qué logra**: El agente puede tomar cuantos pasos necesite (hasta 10). Si el LLM responde con confianza baja, tiene oportunidad de intentar de nuevo con otra herramienta.

**Archivos a tocar**: 1
**Líneas a cambiar**: ~20

---

## Fase 4 — Evaluación post-herramienta (1 archivo)

**Qué**: Después de ejecutar una herramienta, pedirle al LLM que evalúe explícitamente si el resultado es suficiente.

**Dónde**: `agent/agent_runtime.py:254-256`

**Cambio**:
```python
# ANTES
elif parsed["type"] == "tool":
    result = self._execute_tool(parsed)
    working.append({"role": "system", "content": f"Resultado de {parsed['name']}: {result}"})
    final = result
    ...

# DESPUÉS
elif parsed["type"] == "tool":
    result = self._execute_tool(parsed)
    working.append({"role": "system", "content": f"Resultado de {parsed['name']}: {result}"})
    working.append({"role": "system", "content": "Evalúa si el resultado responde la pregunta del usuario. Si sí, responde con reply. Si necesitas más información, usa otra herramienta."})
    # No asignar final aquí — seguir en el loop
    continue
```

**Qué logra**: El LLM no asume que el resultado de la tool es la respuesta final. Evalúa y decide si responde o necesita más pasos.

**Archivos a tocar**: 1
**Líneas a cambiar**: ~5

---

## Resumen de implementación

| Fase | Cambio | Archivos | Líneas | Esfuerzo | Impacto agentico |
|------|--------|----------|--------|----------|-----------------|
| 1 | Coordinador con LLM | 1 | ~10 | 15 min | **Alto** (deja de ser if-else) |
| 2 | Confidence desde LLM | 3 | ~15 | 30 min | Medio (confianza real) |
| 3 | Loop flexible | 1 | ~20 | 30 min | Medio (no truncado) |
| 4 | Evaluación post-tool | 1 | ~5 | 15 min | Medio (cierra el ciclo ReAct) |

**Orden recomendado**: 1 → 4 → 3 → 2

- 1 es el cambio más simple y el que más transforma la arquitectura
- 4 complementa a 1 (sin evaluación, el loop no tiene feedback)
- 3 solo tiene sentido después de 4 (para que el loop sirva)
- 2 es independiente, se puede hacer en cualquier momento

**Tiempo total estimado**: ~1.5 horas de implementación

---

## Lo que NO cambia

- Skills existentes (`calcular`, `consultar_db`, `consultar_faq`, etc.)
- `BaseSkill` abstract
- Rutas de la API
- Frontend
- Persistencia (JSON sigue igual)
- Tests existentes (se agregan, no se modifican)
