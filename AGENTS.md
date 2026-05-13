# Learnings - superagente

## Fuente de datos
- La base de datos SQLite está en `data/demo.db`
- Tabla `productos`: id, nombre, categoria, precio, stock, stock_minimo
- Tabla `ventas`: id, producto_id, cantidad, total, fecha, mes
- **Siempre consultar la DB directamente** con SQL para preguntas sobre inventario, stock, productos, ventas. No usar texto genérico ni suposiciones.

## Handlers (consultas de datos)
- `agent/handlers.py` contiene funciones Python con SQL directo para cada tipo de consulta
- El ruteo usa patrones regex con pesos (mayor peso = más específico), sin LLM
- Si un handler matchea, se ejecuta directo. El LLM solo se usa si ningún handler matchea (charla)
- **NUNCA** usar el LLM para generar SQL, clasificar consultas, ni producir datos de DB
- Para añadir un handler: agregar la función + patrón regex en `_HANDLERS`

## Tests
- `python3 -m pytest tests/test_handlers.py -v` — corre los 13 tests
- Ejecutar SIEMPRE antes y después de tocar `agent/handlers.py` o `agent/agent_runtime.py`
- Si un test falla, el ruteo está mal — arreglar antes de continuar

## Estándar de respuesta
- Respuestas con confianza < 90% son rechazadas automáticamente.
- No responder con datos genéricos o no verificados.
- Si la respuesta requiere datos de DB: consultar primero, responder después.
- Si no se puede verificar con certeza, decirlo explícitamente.
