import sys
sys.path.insert(0, ".")

from agent.intent import clasificar_intencion


def test_conversacion_saludo():
    assert clasificar_intencion("hola") == "conversacion"


def test_conversacion_gracias():
    assert clasificar_intencion("gracias") == "conversacion"


def test_datos_ventas():
    assert clasificar_intencion("ventas de enero") == "datos"


def test_datos_productos():
    assert clasificar_intencion("productos mas vendidos") == "datos"


def test_datos_stock():
    assert clasificar_intencion("stock bajo") == "datos"


def test_atencion_horario():
    assert clasificar_intencion("cual es el horario de atencion") == "atencion"


def test_atencion_factura():
    assert clasificar_intencion("necesito mi factura") == "atencion"


def test_atencion_envio():
    assert clasificar_intencion("cuando llega mi envio") == "atencion"


def test_finanzas_iva():
    assert clasificar_intencion("cual es el iva") == "finanzas"


def test_finanzas_descuento():
    assert clasificar_intencion("descuento por volumen") == "finanzas"


def test_otro():
    assert clasificar_intencion("que opinas de la musica clasica") == "otro"


def test_vacio():
    assert clasificar_intencion("") == "otro"


if __name__ == "__main__":
    test_conversacion_saludo()
    test_conversacion_gracias()
    test_datos_ventas()
    test_datos_productos()
    test_datos_stock()
    test_atencion_horario()
    test_atencion_factura()
    test_atencion_envio()
    test_finanzas_iva()
    test_finanzas_descuento()
    test_otro()
    test_vacio()
    print("\n✅ TODOS LOS TESTS DE INTENT PASARON")
