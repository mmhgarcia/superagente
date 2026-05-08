# Plan: Skills Ejecutables

## Objetivo
Convertir skills de texto descriptivo a funciones Python ejecutables.

## Arquitectura

```
Usuario: "calcula 15% de 3400"
       ↓
Agente recibe el mensaje
       ↓
Router de skills decide:
  └── ¿Hay una skill que pueda ejecutar esto?
        ├── Sí → ejecuta función Python → resultado exacto
        └── No → responde con LLM (como hoy)
       ↓
Devuelve respuesta al usuario
```

## Tareas

### Tarea 1: Definir interfaz de skill ejecutable
- [ ] Crear `agent/skills/` como carpeta de skills
- [ ] Definir clase base `BaseSkill` con método `match(mensaje) → bool` y `execute(mensaje) → str`
- [ ] Registrar skills en SkillStore como ejecutables

### Tarea 2: Implementar skills ejecutables
- [ ] **skill_calcular**: extrae operación matemática → `eval()` seguro → resultado
- [ ] **skill_resumir**: toma el historial y pide al LLM que resuma
- [ ] **skill_formatear**: estructura la respuesta en JSON/listas
- [ ] Dejar `base_chat` como está (solo LLM)

### Tarea 3: Router de skills en AgentRuntime
- [ ] Modificar `ask()` para que pruebe skills antes del LLM
- [ ] Si una skill hace `match()`, ejecutarla y devolver resultado
- [ ] Si ninguna skill hace match, responder con LLM como hoy
- [ ] Agregar logging de qué skill se ejecutó

### Tarea 4: Tests
- [ ] Tests para cada skill ejecutable
- [ ] Test del router de skills
- [ ] Test de integración: agente con skills mixtas

## Skills propuestas para este sprint

| Skill | Disparador | Acción |
|-------|-----------|--------|
| `calcular` | "cuánto es X% de Y", "suma X+Y" | Evalúa expresión matemática |
| `resumir` | "resume", "resumen" | Envía historial al LLM pidiendo resumen |
| `formatear` | "como lista", "tabla", "enumera" | Estructura la respuesta previa |
