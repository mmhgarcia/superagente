# Learnings - superagente

## Fuente de datos
- La base de datos SQLite está en `data/demo.db`
- Tabla `productos`: id, nombre, categoria, precio, stock, stock_minimo
- Tabla `ventas`: id, producto_id, cantidad, total, fecha, mes
- **Siempre consultar la DB directamente** con SQL para preguntas sobre inventario, stock, productos, ventas. No usar texto genérico ni suposiciones.

## Estándar de respuesta
- Respuestas con confianza < 90% son rechazadas automáticamente.
- No responder con datos genéricos o no verificados.
- Si la respuesta requiere datos de DB: consultar primero, responder después.
- Si no se puede verificar con certeza, decirlo explícitamente.
