from . import llm


_CATEGORIES = ("conversacion", "datos", "atencion", "finanzas", "otro")

_FALLBACK_MAP = {
    "cortes": "conversacion",
    "saludo": "conversacion",
    "agradec": "conversacion",
    "desped": "conversacion",
    "producto": "datos",
    "venta": "datos",
    "stock": "datos",
    "inventario": "datos",
    "precio": "datos",
    "horario": "atencion",
    "factur": "atencion",
    "devoluc": "atencion",
    "envio": "atencion",
    "pago": "atencion",
    "garant": "atencion",
    "contacto": "atencion",
    "iva": "finanzas",
    "impuest": "finanzas",
    "presupuest": "finanzas",
    "contabilidad": "finanzas",
    "descuento": "finanzas",
}

_PROMPT = (
    "Clasifica el mensaje en UNA palabra: conversacion, datos, atencion, finanzas u otro.\n"
    "- conversacion: saludos, agradecimientos, cortesía\n"
    "- datos: productos, ventas, stock, precios, inventario\n"
    "- atencion: horarios, facturas, devoluciones, envíos, pagos\n"
    "- finanzas: IVA, impuestos, presupuestos, descuentos\n"
    "- otro: cualquier otro tema\n\n"
    "Mensaje: {message}\n"
    "Categoría:"
)


def _mapear_fallback(raw):
    raw_lower = raw.lower()
    for cat_name in _CATEGORIES:
        if cat_name in raw_lower:
            return cat_name
    for key, cat in _FALLBACK_MAP.items():
        if key in raw_lower:
            return cat
    return None


def clasificar_intencion(message):
    if not message or not message.strip():
        return "otro"
    raw = llm.generate(_PROMPT.format(message=message.strip()), system_prompt="", temperature=0.0)
    if not raw:
        return "otro"
    resultado = _mapear_fallback(raw)
    return resultado or "otro"
