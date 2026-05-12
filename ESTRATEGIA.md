# Estrategia Arquitectónica: ¿Refactor o Rediseño?

**Pregunta**: ¿Es más conveniente, funcional y escalable mantener Superagente tal como está, o rediseñarlo como Superagente II adoptando el modelo arquitectónico de rag_project?

---

## 1. Diagnóstico: Estado Actual de Superagente

### 1.1 Deuda Técnica Identificada

| # | Problema | Archivo | Impacto |
|---|----------|---------|---------|
| 1 | **God Class** — `AgentRuntime` hace CRUD, prompts, tool execution, routing, persistencia | `agent/agent_runtime.py:42` | Violación SRP. Cualquier cambio toca todo. Imposible testear aisladamente. |
| 2 | **Sin DI** — Skills globales en `_EXECUTABLE_SKILLS`, runtime importado como singleton | `agent/agent_runtime.py:15`, `routes/agents.py:5` | No se puede mockear. Tests frágiles. Acoplamiento全局. |
| 3 | **LLM síncrono** — `requests.post()` bloquea event loop de FastAPI | `agent/llm.py:37` | Bajo carga, todas las requests se encolan. Una llamada lenta bloquea todo. |
| 4 | **TCP Proxy hack** — `ollama_forward.py` como proceso separado | `scripts/ollama_forward.py` | Punto extra de fallo, mantenimiento, complejidad operativa. |
| 5 | **Routing hardcoded** — `_route_message()` con keywords quemadas en código | `agent/agent_runtime.py:202-214` | Cada nuevo agente requiere modificar código. No escalable. |
| 6 | **Sin telemetría** — Cero métricas de latencia, errores, uso | — | Ciego en producción. No se puede optimizar lo que no se mide. |
| 7 | **Sin caché** — Cada llamada ejecuta el LLM completo | — | Latencia innecesaria en preguntas repetidas. Costo computacional duplicado. |
| 8 | **Persistencia JSON** — `agents.json` crece indefinidamente | `data/agents.json` | Sin consultas, sin índices. El archivo completo se lee/escribe en cada operación. |
| 9 | **LLM genera SQL** — Sin validación de esquema ni límites | `agent/skills/db.py:30` | Riesgo de seguridad. Queries ineficientes. Datos incorrectos. |
| 10 | **Confidence ficticio** — Solo 4 valores (20/50/90/100) sin base real | `agent/agent_runtime.py:235-266` | Engañoso. No refleja confianza real del modelo. |
| 11 | **Sin schemas de respuesta** — Las rutas devuelven dicts sin validar | `routes/agents.py:29-76` | Contratos API implícitos. Breaking changes silenciosos. |
| 12 | **Sin graceful degradation** — Si el LLM falla, retorna `None` | `agent/llm.py:45-48` | El frontend recibe null sin saber por qué. |

### 1.2 ¿Por qué pasó esto?

Superagente evolucionó por prototipado rápido. Funciona, pero:

> "Nada es tan permanente como una solución temporal."

El TCP proxy, el routing hardcodeado, la persistencia JSON — todo comenzó como "lo pongo así por ahora y lo arreglo después". Ese "después" nunca llegó porque el sistema **funcionaba**. Pero ahora que se quiere escalar, estas decisiones pesan.

---

## 2. Referencia: ¿Qué Hace Bien rag_project?

### 2.1 Fortalezas Arquitectónicas

| Práctica | rag_project | Superagente |
|----------|-------------|-------------|
| Separación por capas | `rag/`(domain) + `api/`(HTTP) + `telemetry/`(infra) | God class `agent_runtime.py` |
| Dependency Injection | `dependencies.py` con `RAGEngineDep` | Singleton global importado |
| Schemas Pydantic | Cada response con tipos válidos | Dicts sin validar |
| Async nativo | `httpx.AsyncClient` + async routes | `requests` síncrono |
| Telemetría | SQLite con métricas por query | Cero |
| Caché | LRU + TTL, thread-safe | Cero |
| Background jobs | ThreadPool + SSE streaming | No existe |
| Error handling | `RAGError` + try/except granular | `return None` o `"Error: ..."` |
| Config | Pydantic Settings (env vars) | Archivo JSON + load_config() |
| Testeabilidad | DI permite mockear dependencias | Singleton global impide aislamiento |

### 2.2 Por qué rag_project está mejor estructurado

rag_project fue diseñado (no evolucionado). Tiene una **intención arquitectónica clara** desde el inicio. Superagente, en cambio, **creció orgánicamente** — lo que llevó a:

- Funciones que hacen demasiado
- Dependencias ocultas
- Caminos de error no cubiertos
- Falta de boundaries entre capas

---

## 3. Análisis: Refactor Incremental vs. Rediseño

### 3.1 ¿Se puede refactorizar incrementalmente?

Para llevar Superagente al nivel de rag_project, habría que:

1. Extraer `AgentRuntime` → dividir en 3-4 clases (gestión de agentes, ejecución de tools, orquestación de conversación, routing)
2. Introducir DI → cambiar cómo se instancian skills y runtime
3. Reemplazar `requests` → `httpx.AsyncClient`
4. Eliminar TCP proxy → conectar a Ollama directamente
5. Añadir schemas → tocar todas las rutas
6. Añadir telemetría → nuevo módulo, tocar `ask()` y `_execute_tool()`
7. Añadir caché → nuevo módulo, tocar `ask()`
8. Reemplazar JSON → SQLite, migrar datos existentes
9. Reemplazar routing hardcoded → strategy pattern configurable
10. Limitar SQL generado por LLM → cambiar contrato de `consultar_db`

**Problema**: Cada uno de estos cambios toca `agent_runtime.py`. Es un cuello de botella. El refactor sería esencialmente un **rediseño en fases** pero con el riesgo constante de romper algo que funciona.

### 3.2 Comparación de esfuerzos

| Escenario | Esfuerzo estimado | Riesgo | Resultado |
|-----------|-------------------|--------|-----------|
| **Refactor incremental** | 3-4 sprints | Alto (regresiones constantes) | Arquitectura mejorada pero con cicatrices |
| **Rediseño (Superagente II)** | 2-3 sprints | Medio (greenfield) | Arquitectura limpia desde el día 1 |

> El refactor no es más barato que el rediseño porque la deuda es **arquitectónica**, no local. Cambiar una god class requiere entenderla entera, no solo una parte.

### 3.3 Lo que se salva (no hay que reescribir)

| Componente | Estado | Acción |
|------------|--------|--------|
| Skills: `calcular.py`, `faq.py`, `resumir.py` | Bien | Migrar tal cual |
| Skill: `consultar_db.py` | Funcional | Migrar con mejoras de seguridad |
| Skill: `consultar_rag.py` | Funcional | Migrar, mejorar response |
| `BaseSkill` abstract | Bien | Migrar tal cual |
| Frontend React | Bien estructurado | Migrar componentes |
| `data/faq.json` | Datos | Migrar a SQLite |
| `data/demo.db` | Datos | Migrar tal cual |
| Tests existentes | Básicos | Reescribir con nueva arquitectura |

---

## 4. Propuesta: Superagente II

### 4.1 Arquitectura Propuesta

Adoptando los patrones de rag_project:

```
┌────────────────────────────────────────────────────────────┐
│                    Superagente II                           │
│                                                            │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐       │
│  │  api/        │  │  agent/     │  │  telemetry/  │       │
│  │  (FastAPI)   │──│  (core)     │──│  (SQLite)    │       │
│  │  ┌─────────┐ │  │  ┌───────┐ │  │  ┌────────┐  │       │
│  │  │ health  │ │  │  │service│ │  │  │metrics │  │       │
│  │  │ agents  │ │  │  │executor│  │  │  │queries │  │       │
│  │  │ skills  │ │  │  │router │ │  │  └────────┘  │       │
│  │  │ config  │ │  │  │llm    │ │  └──────────────┘       │
│  │  └─────────┘ │  │  └───────┘ │                          │
│  └─────────────┘  └─────────────┘                          │
│       │                   │                                │
│       ▼                   ▼                                │
│  ┌─────────────┐  ┌──────────────┐                         │
│  │  schemas/   │  │  skills/     │                         │
│  │  Pydantic   │  │  (pluggable) │                         │
│  └─────────────┘  └──────────────┘                         │
│                                                            │
│  ┌─────────────┐  ┌──────────────┐                         │
│  │  cache/     │  │  frontend/   │                         │
│  │  (LRU+TTL)  │  │  (React)     │                         │
│  └─────────────┘  └──────────────┘                         │
└────────────────────────────────────────────────────────────┘
```

### 4.2 Módulos y Responsabilidades

| Módulo | Responsabilidad | Similar a rag_project |
|--------|-----------------|----------------------|
| `agent/service.py` | CRUD de agentes, orquestación de conversación | `rag/rag_engine.py` |
| `agent/executor.py` | Ejecución de tools (skills) | — (nuevo) |
| `agent/router.py` | Routing de mensajes a agentes (pluggable, no hardcoded) | — (nuevo) |
| `agent/llm.py` | Cliente LLM async (Ollama directo, sin proxy) | `rag/rag_engine.py:query_model()` |
| `agent/skills/` | Skills ejecutables (BaseSkill + implementaciones) | — (existentes) |
| `api/routers/` | Endpoints REST (agents, skills, config, health) | `api/routers/` |
| `api/schemas/` | Pydantic models para request/response | `api/schemas.py` |
| `api/dependencies.py` | DI con `AgentServiceDep` | `api/dependencies.py` |
| `telemetry/` | SQLite con métricas de cada interacción | `telemetry/database.py` |
| `cache/` | LRU cache para respuestas del LLM | `rag/cache.py` |
| `frontend/` | React UI (existe, migrar) | `panel/` |

### 4.3 Flujo Rediseñado

```
POST /agents/{id}/ask  {message}
    │
    ▼
api/routers/agents.py → AgentServiceDep (DI)
    │
    ▼
agent/service.py :: ask()
    ├─ 1. Cache lookup → HIT → retorna
    ├─ 2. Router decide: ¿delegar o responder directo?
    │     ├─ Routing basado en configuración (no hardcoded)
    │     └─ Si delegar → AgentService.ask(otro_agente, mensaje)
    ├─ 3. Build system prompt (service)
    ├─ 4. LLM call (llm.py, async, con métricas)
    ├─ 5. ¿Tool call? → executor.execute()
    ├─ 6. Si tool devolvió datos → LLM call de síntesis (opcional)
    ├─ 7. Cache SET
    └─ 8. Telemetry SAVE (latencia, tool usada, confidence real)
```

### 4.4 Diferencias Clave con el Actual

| Aspecto | Superagente actual | Superagente II |
|---------|-------------------|----------------|
| **Routing** | `_route_message()` hardcoded | Router pluggable (config en JSON/DB) |
| **LLM** | `requests` síncrono + TCP proxy | `httpx.AsyncClient` directo a Ollama |
| **Skills** | Dict global en runtime | Registro vía DI + discovery automático |
| **Persistencia** | JSON (agents.json) | SQLite (agents + config + history) |
| **Telemetría** | No existe | SQLite con métricas por request |
| **Cache** | No existe | ResponseCache (LRU + TTL) |
| **Schemas** | Algunos Pydantic en routes/ | Schemas completos para todo el API |
| **Error handling** | return None o "Error: ..." | Excepciones específicas + HTTP status codes |
| **Tests** | 3 tests básicos | Tests unitarios + integración desde día 1 |
| **Config** | JSON + load_config() | Pydantic Settings (env vars + .env) |

### 4.5 Lo que NO cambia

- **Modelo de skills plugables** — `BaseSkill` con `match()` + `execute()` + `execute_tool()`
- **Agentes dinámicos** — Creación/configuración vía API
- **Coordinador que delega** — Patrón de orquestación se mantiene
- **Frontend React** — Se migra, no se reescribe
- **Demo data** — `data/demo.db` se mantiene como está

---

## 5. Recomendación Final

**Rediseñar como Superagente II.**

### Argumentos

| Criterio | Seguir igual | Superagente II |
|----------|-------------|----------------|
| **Conveniencia** | Cada nueva feature toca god class. Frustrante. | Módulos claros. Añadir feature = tocar 1 módulo. |
| **Funcionalidad** | Sin telemetría, sin cache, sin async. Limitado. | Telemetría, cache, async, routing dinámico. |
| **Escalabilidad** | Una request bloquea todo (sync + sin cache). | Async + cache = throughput ×10. |
| **Mantenibilidad** | Deuda técnica empeora con cada cambio. | Deuda cero si se respeta la arquitectura. |
| **Testeabilidad** | Singleton global → tests frágiles. | DI → mocks → tests aislados. |

### Plan sugerido

```
Sprint 1: Fundación
├─ Estructura de proyecto (agent/, api/, telemetry/, cache/)
├─ DI pattern (dependencies.py)
├─ LLM client async (httpx, sin proxy)
└─ Schemas Pydantic

Sprint 2: Core
├─ AgentService (CRUD + orquestación)
├─ SkillExecutor (tool execution con DI)
├─ Router pluggable (no hardcoded)
└─ Persistencia SQLite

Sprint 3: Calidad
├─ Telemetría (adoptar modelo de rag_project)
├─ Cache LRU+TTL (adoptar código de rag_project)
├─ Error handling robusto
└─ Tests (unitarios + integración)

Sprint 4: Migración
├─ Migrar frontend React existente
├─ Migrar datos (JSON → SQLite)
├─ Migrar skills existentes
└─ E2E testing
```

### Riesgos del rediseño

- **Tiempo muerto**: Durante el desarrollo, las nuevas features no se pueden hacer en el actual.
  - Mitigación: Mantener Superagente actual funcionando en paralelo hasta que Superagente II esté listo.
- **Overengineering**: Tentación de hacerlo "demasiado abstracto".
  - Mitigación: Adoptar patrones de rag_project, no inventar nuevos.
- **Pérdida de funcionalidad**: Algo que funciona hoy podría no migrarse correctamente.
  - Mitigación: E2E tests comparativos antes del switch.

---

## 6. Conclusión

> Superagente actual es un prototipo funcional. rag_project demuestra que el equipo sabe hacer arquitectura sólida. Superagente II es aplicar ese mismo estándar al dominio de agentes.

La pregunta no es si se puede refactorizar (se puede), sino **si vale la pena**. Refactorizar incrementalmente una god class lleva el mismo esfuerzo que rediseñar, pero con más riesgo y un resultado peor. El rediseño es la opción correcta.
