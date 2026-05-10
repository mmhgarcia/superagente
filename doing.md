# Plan: Orquestador (Coordinador)

## Goal
El Coordinador recibe cualquier request, lo clasifica, lo delega al agente especializado correcto, y devuelve la respuesta al usuario.

## Slices

### Slice 1 — Tool `delegar` ✅
Crear un tool ejecutable que llame a `AgentRuntime.ask()` de otro agente.
- Input: `{"agente": "calculista", "mensaje": "15% de 3400"}`
- Output: la respuesta del agente delegado
- Nombre: `delegar`

### Slice 2 — Crear agentes especializados ✅
- `calculista` (existe, con skill `calcular`)
- `finanzas` (creado, con skill `calcular`)
- `atencion` (creado, solo LLM)

### Slice 3 — System prompt del Coordinador ✅
- Clasifica, delega vía `delegar` tool, responde

### Slice 4 — Ruta por defecto ⬜
El frontend inicia con el Coordinador preseleccionado.
- Modificar `AgentChat.jsx` para que `selected` arranque con `coordinador`

### Slice 5 — Pruebas ✅
- "cuanto es 15% de 3400?" → coordinador → calculista → "510" ✅
- "cuanto es el IVA de 200 al 21%" → coordinador → finanzas → "42" ✅

## Notas
- Latencia: cada LLM call ~1-2 min, delegación encadena 2 → total 3-5 min
- Forwarder: `setsid python3 scripts/ollama_forward.py &`
- consultar_db: el LLM genera SQL libremente. Pendiente: controlar/limitar los campos devueltos por las consultas.


------------------
manejo de agemntes custom (skill muy especifico)
es viable
