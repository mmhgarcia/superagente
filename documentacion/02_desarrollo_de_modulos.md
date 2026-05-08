# Fase 2: Desarrollo de Módulos (Smart Factory)

## Objetivo
Construir agentes funcionales con estado, memoria y capacidad de conversación real, más el Skill Store que los configura.

---

## Tarea 2.1: Implementar el Skill Store

### Subtarea: Modelo de datos y almacenamiento
- [ ] Definir esquema de skills (id, nombre, descripción, función, parámetros)
- [ ] Implementar Skill Store en memoria (JSON) para PoC
- [ ] Crear API REST: listar skills, obtener skill, registrar skill
- [ ] Implementar asignación de skills a agentes

### Subtarea: Catálogo inicial de skills
- [ ] `base_chat`: Conversación básica
- [ ] `calcular`: Operaciones matemáticas simples
- [ ] `buscar`: Búsqueda en web (simulada)
- [ ] `formatear`: Dar formato estructurado a respuestas

---

## Tarea 2.2: Implementar el Agent Runtime

### Subtarea: Modelo de agente
- [ ] Definir clase Agent con estado, memoria, skills asignadas
- [ ] Implementar memoria de sesión (contexto conversacional)
- [ ] Implementar almacenamiento de agentes (en memoria)

### Subtarea: API de agentes
- [ ] `POST /agents/create` — Crear agente (refactor desde `/generate_agent`)
- [ ] `GET /agents` — Listar agentes
- [ ] `GET /agents/{id}` — Ver detalle de agente
- [ ] `DELETE /agents/{id}` — Eliminar agente

---

## Tarea 2.3: Implementar el chat real

### Subtarea: Percepción
- [ ] Parsear mensajes del usuario
- [ ] Detectar intención básica
- [ ] Validar entrada y sanitizar

### Subtarea: Razonamiento
- [ ] Construir system prompt con personalidad y skills del agente
- [ ] Integrar historial conversacional en el prompt
- [ ] Enviar a LLM (TinyLlama) y recibir respuesta
- [ ] Manejar errores y timeouts

### Subtarea: Acción
- [ ] Ejecutar skills asociadas al agente cuando corresponda
- [ ] Devolver respuesta formateada

### Subtarea: API de chat
- [ ] `POST /agents/{id}/ask` — Enviar mensaje y recibir respuesta
- [ ] `GET /agents/{id}/history` — Ver historial de conversación

---

## Tarea 2.4: Conectar frontend al chat real

- [ ] AgentChat.jsx: enviar mensajes a `POST /agents/{id}/ask`
- [ ] Mostrar respuestas en tiempo real
- [ ] Mostrar indicador de "pensando..."
- [ ] Mostrar historial de conversación

---

## Criterios de aceptación
- [ ] Skill Store funcional con 4+ skills
- [ ] Agentes con estado y memoria persistente
- [ ] Chat real con LLM funcional
- [ ] Frontend conectado al chat real
- [ ] Tests unitarios para módulos core
- [ ] Manejo de errores y timeouts
