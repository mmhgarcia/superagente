# Estrategias de Integración: Superagente ↔ RAG Project

## Contexto

- **Superagente**: Plataforma de agentes con orquestación, skills ejecutables, LLM vía Ollama.
- **RAG Project**: Sistema RAG independiente con ChromaDB, LM Studio, API REST propia, panel React propio.
- Ambos coexisten en el mismo repositorio pero como dos aplicaciones separadas.

Actualmente existe un skill `consultar_rag` que llama por HTTP a `$RAG_API_URL/query`. Es funcional pero subóptimo. Este documento analiza estrategias de integración más profundas.

---

## Opción 1: Integración por API (Acoplamiento vía HTTP) — Ya existe, mejorable

### Cómo funciona hoy
```
Superagente (skill consultar_rag) ──HTTP──► RAG Project (/api/query)
```

### Lo que ya está listo
- `consultar_rag.py` llama `POST /api/query` con `{"query": msg, "top_k": 5}`.
- RAG Project ya expone `/api/query`, `/api/models`, `/api/ingest`, `/api/health`.
- La skill se activa por keywords: "rag", "buscar", "documento", "informe", "manual", "pdf", etc.

### Mejoras necesarias
| Problema | Solución |
|----------|----------|
| No devuelve fuentes/metadata | Extender respuesta para incluir `sources` |
| Sin integración con el orquestador | Crear agente "documentos" que use `consultar_rag` como tool |
| `RAG_API_URL` hardcodeada en env var | Manejo más robusto (config desde superagente) |
| Timeout fijo de 30s | Configurable |
| Sin control de cache | El RAG ya cachea, pero el skill no lo sabe |

### Recomendación
**✅ Opción válida para producción si ambos servicios corren separados.** Es la de menor acoplamiento pero introduce latencia de red y un punto de fallo adicional.

**Flujo ideal**:
```
Usuario → Coordinador → Agente "documentos" (skill consultar_rag) → RAG API → LM Studio
```

---

## Opción 2: Integración como Módulo Python (Acoplamiento vía import)

### Cómo funciona
```
Superagente (AgentRuntime)
    └── import RAGEngine desde rag_project/rag/rag_engine.py
```

### Ventajas
- **Latencia cero de red** — llamada directa a RAGEngine.answer_question()
- **Sin servicio separado** — no hay que levantar uvicorn aparte
- **Acceso directo a telemetría** — las métricas RAG pueden alimentar el loop del agente
- **Sin serialización/deserialización JSON** — objetos Python directos
- **Cache compartido** — el agente puede saber si una respuesta viene de cache

### Cambios necesarios
1. Ajustar `sys.path` o instalar `rag_project/` como paquete (add `setup.py` o `pyproject.toml`)
2. Modificar `consultar_rag.py` para importar `RAGEngine` directamente
3. Pasar dependencias: `rag_project/requirements.txt` tiene `langchain`, `chromadb`, etc.
4. Resolver conflictos de dependencias con superagente (ver más abajo)
5. El RAG Engine actualmente usa LM Studio; se podría parametrizar para usar Ollama (el LLM de superagente)

### Desventajas
- **Dependencias pesadas**: langchain, chromadb, sentence-transformers se suman al entorno de superagente
- **Recursos**: ChromaDB carga modelos en memoria (all-MiniLM-L6-v2 ~400MB)
- **Acoplamiento fuerte**: cambios en RAGEngine pueden romper superagente
- **Thread safety**: RAGEngine no está diseñado para ser usado desde múltiples hilos (su cache usa `threading.Lock`, pero el vector store no)

### Recomendación
**⚠️ Para entornos pequeños/dev.** No recomendado para producción por el peso de dependencias y recursos. Ideal para un monolito con pocos usuarios.

```python
# Ejemplo conceptual — consultar_rag.py v2
from rag.rag_engine import RAGEngine

engine = RAGEngine(
    chroma_db_path="rag_project/rag/chroma_db",
    lm_studio_url="http://localhost:1234",
)

class ConsultarRagSkill(BaseSkill):
    def execute_tool(self, args):
        respuesta = engine.answer_question(args["query"])
        return respuesta["answer"]
```

---

## Opción 3: Agente RAG Dedicado en Superagente (Integración vía Orquestador)

### Cómo funciona
Crear un agente especializado llamado `"documentos"` (o `"consulta_documental"`) dentro de superagente, que tenga el skill `consultar_rag`. El coordinador delega a este agente automáticamente.

### Lo que ya existe
- El coordinador ya tiene routing por keywords (`_route_message()`)
- Se pueden añadir keywords como: "documento", "manual", "procedimiento", "pdf", "norma"
- El agente se crea con `POST /agents/create`

### Lo que falta
```python
# En agent_runtime.py, _route_message() — añadir ruta
routes = {
    "datos": [...],
    "atencion": [...],
    "finanzas": [...],
    "documentos": ["documento", "manual", "procedimiento", "pdf",
                    "norma", "política", "instructivo", "guía", "reglamento"],
}
```

### Ventajas
- **Mínimo esfuerzo** — solo añadir rutas y crear el agente
- **Alineado con arquitectura existente** — el orquestador ya hace esto
- **Experiencia unificada** — el usuario no sabe que hay un RAG detrás

### Desventajas
- Depende de Opción 1 o 2 para el backend real
- Sin esto, `consultar_rag` solo se activa si el LLM decide usarlo explícitamente

### Recomendación
**✅ Hacer esto independientemente de la opción de integración elegida.** Es bajo esfuerzo y alto impacto.

---

## Opción 4: Compartir LLM (Ollama como backend de RAG)

### Problema actual
- **Superagente** usa Ollama (`qwen2.5-coder:7b`) en puerto 11434.
- **RAG Project** usa LM Studio en puerto 1234.

Son **dos LLMs distintos** ocupando RAM/VRAM por separado.

### Solución
Configurar el RAG Engine para usar Ollama en lugar de LM Studio. Ambas exponen API compatible con OpenAI (`/v1/chat/completions`).

### Cambio mínimo en `rag_engine.py`
```python
# Cambiar base_url de LM Studio a Ollama
lm_studio_url = "http://localhost:11434/v1"
# El payload es casi idéntico
```

### Ventajas
- **Un solo LLM** en lugar de dos — ahorro de ~8GB de RAM/VRAM
- Menos procesos en segundo plano
- El RAG usa el mismo modelo que el agente — consistencia

### Desventajas
- LM Studio permite cambiar modelos más fácilmente (UI gráfica)
- Ollama no tiene la misma UX para gestión de modelos

### Recomendación
**✅ Hacerlo si los recursos son limitados.** Configurable vía variable de entorno para no perder flexibilidad.

---

## Opción 5: Fusión de Frontends (Panel Unificado)

### Problema actual
- Superagente tiene su propio frontend React (`frontend/`)
- RAG Project tiene su propio frontend React (`panel/`)
- El usuario debe usar dos URLs distintas

### Solución A: Iframe
```jsx
// En el frontend de superagente, un tab más
<Tab label="Documentos RAG">
  <iframe src="http://localhost:8001" />
</Tab>
```

### Solución B: Proxy inverso (nginx/Caddy)
```
superagente.local/         → frontend superagente
superagente.local/rag/     → frontend RAG (proxy reverso)
superagente.local/api/rag/ → RAG API
```

### Solución C: Integración profunda (componentes React)
Extraer `ChatPanel.tsx` del RAG y montarlo como un skill UI dentro de superagente. Esto requiere que ambos usen el mismo framework (React 19 + Vite, lo cual es cierto).

### Recomendación
**✅ Solución B (proxy) para empezar.** Rápido, no requiere cambios de código. Solución C para una experiencia realmente unificada.

---

## Opción 6: Skill Híbrido — RAG + SQLite (Consulta Unificada)

### Problema
Actualmente hay datos separados:
- **RAG Project**: Documentos (PDF, DOCX, procedimientos)
- **Superagente DB**: Productos y ventas estructurados (SQLite)

Un usuario podría preguntar: *"¿Qué dice el manual sobre el producto más vendido?"*

### Solución
Crear un skill `consultar_unificado` que:
1. Consulta SQLite (`consultar_db`) para obtener datos estructurados
2. Consulta RAG (`consultar_rag`) con el resultado como contexto
3. Síntesis: usa el LLM para combinar ambas fuentes

### Flujo
```
Usuario: "¿El procedimiento menciona algo sobre la Laptop Gamer X1?"
    ↓
Skill unificado:
    1. consultar_db → "SELECT * FROM productos WHERE nombre LIKE '%Laptop%'"
    2. consultar_rag → "buscar Laptop Gamer X1 en documentos"
    3. LLM sintetiza: "Según el manual de procedimientos, la Laptop Gamer X1..."
```

### Recomendación
**⚠️ Para futura iteración.** Es de alto valor pero requiere diseño cuidadoso (evitar loops, manejar contexto grande).

---

## Tabla Comparativa

| Opción | Esfuerzo | Acoplamiento | Recursos | Latencia | Unificación |
|--------|----------|--------------|----------|----------|-------------|
| 1. API (actual) | Bajo | Bajo | 2 servicios | Red | Baja |
| 2. Módulo Python | Medio | Alto | 1 proceso | Cero | Alta |
| 3. Agente dedicado | **Muy bajo** | Ninguno | Igual | Igual | **Alta (UX)** |
| 4. Compartir LLM | Bajo | Medio | -8GB RAM | Igual | Media |
| 5. Frontend unificado | Medio | Bajo | Igual | Igual | **Alta (UX)** |
| 6. Skill híbrido | Alto | Medio | Igual | Mayor | **Muy alta** |

---

## Recomendación de Implementación por Fases

### Fase 1 (inmediata) — Bajo esfuerzo, alto impacto
1. **Opción 3**: Crear agente "documentos" con ruta en el coordinador + keywords
2. **Opción 1 mejorada**: Hacer que `consultar_rag` devuelva fuentes y metadata
3. **Configuración**: Añadir `RAG_API_URL` a `data/config.json` de superagente (no solo env var)

### Fase 2 (corto plazo) — Optimización de recursos
4. **Opción 4**: Hacer que el RAG pueda usar Ollama como backend LLM (configurable)
5. Considerar si se necesita un LLM separado o uno compartido

### Fase 3 (medio plazo) — Experiencia unificada
6. **Opción 5B**: Proxy reverso para unificar frontends bajo una misma URL
7. Evaluar si `consultar_rag` como módulo Python (Opción 2) aporta suficiente valor vs. complejidad

### Fase 4 (largo plazo) — Integración profunda
8. **Opción 6**: Skill híbrido RAG+SQLite para consultas cross-dominio
9. Telemetría unificada: métricas RAG visibles en el panel de superagente
