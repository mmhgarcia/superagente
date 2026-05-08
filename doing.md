# Doing — Tool-use dinámico

## Goal
Que el LLM decida qué skill ejecutar y cuándo, en vez del router secuencial hardcodeado.

## Plan (7 slices)

### Slice 1 — Formato tool-call
Definir JSON que el LLM debe emitir en cada respuesta:
```json
{"tool": "calcular", "args": {"expr": "sin(30)"}}
```
o si no necesita tool:
```json
{"reply": "El seno de 30° es 0.5"}
```

### Slice 2 — System prompt
Cambiar de "tus habilidades son..." a instrucción explícita: "responde ÚNICAMENTE con JSON usando tool o reply".

### Slice 3 — Parser
Extraer el JSON de la respuesta del LLM (viene crudo o envuelto en ```json ... ```).

### Slice 4 — Ejecutor
Tomar `tool + args`, llamar `_EXECUTABLE_SKILLS[tool].execute(...)`, devolver resultado.

### Slice 5 — Loop agente
Si el LLM pidió tool: ejecutar → inyectar resultado como observación → llamar LLM otra vez → repetir hasta que responda con `reply`.

### Slice 6 — Límite
Máx 3 iteraciones. Si se pasa, devolver último `reply` o mensaje de error.

### Slice 7 — Pruebas
Pregunta multi-paso: _"calcula el IVA de 200 si la tasa es 21% y sumale 50"_
1. tool call → IVA(200, 21) → 42
2. tool call → suma(42, 50) → 92
3. reply → "El resultado es 92"

## Status

- [x] Slice 1 — Formato tool-call
  - JSON: `{"thought":"...","tool":"calcular","args":{"query":"..."}}` o `{"thought":"...","reply":"..."}`
  - Catálogo inicial: `calcular(query)`, `resumir(texto)`
  - Regla: un tool o reply por respuesta
- [x] Slice 2 — System prompt
  - Implementado: instrucción JSON + herramientas dinámicas
  - Probado: LLM responde con `{"reply": "..."}`
## Notas
- Forwarder: `setsid python3 scripts/ollama_forward.py &` (auto-reinicio ante crash)
- Backend intenta conectar a `host.docker.internal:11435` (forwarder)
- Alerta en frontend si LLM caído

- [x] Slice 3 — Parser
  - Creado: `agent/parser.py` (extrae JSON crudo o envuelto en ```)
  - 9 tests unitarios pasando
  - Integrado en `ask()`: devuelve solo `reply` al frontend
- [x] Slice 4 — Ejecutor
  - LLM llama tool con `{"tool":"calcular","args":{"query":"..."}}`
  - Backend ejecuta `skill.execute_tool(args)` y devuelve resultado
  - Probado: "15% de 3400" → skill devuelve "510.00"
- [x] Slice 5 — Loop agente
  - Hasta 3 iteraciones: tool → observación → LLM → reply
  - Probado: raíz cuadrada 144 + seno 30 → tool call → observación → "12.5"
- [x] Slice 6 — Límite
  - `max_steps = 3`, corta automáticamente
- [x] Slice 7 — Pruebas
  - "calcula el IVA de 200 si la tasa es 21% y sumale 50" → tool x2 → 92 ✅
  - "calcula el seno de 30 grados y sumale 1" → tool x2 → 1.5 ✅
  - Fix: agregado `sen` como alias trigonométrico + soporte paréntesis
