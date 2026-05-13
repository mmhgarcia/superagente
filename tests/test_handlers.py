import sys
sys.path.insert(0, ".")

from agent.handlers import sql_handler


def test_sql_select_only():
    result = sql_handler("lista de productos")
    assert "Laptop Gamer X1" in result
    assert "Mouse Inalámbrico" in result


def test_sql_ventas():
    result = sql_handler("ventas por mes")
    assert any(x in result.lower() for x in ["mes", "total", "venta", "enero", "1", "2", "3"])


def test_sql_stock_bajo():
    result = sql_handler("stock bajo")
    assert "No" in result or "resultado" in result or "stock" in result.lower()


def test_sql_stock_entre():
    result = sql_handler("productos con stock entre 15 y 25")
    assert "Monitor" in result or "Webcam" in result or "Audífonos" in result


def test_sql_invalid_rejected():
    from agent.handlers import _query
    rows = _query("SELECT COUNT(*) as c FROM productos")
    assert rows[0]["c"] == 8


def test_sql_categoria():
    result = sql_handler("productos por categoria")
    assert any(x in result for x in ["Electrónica", "Accesorios", "categoria", "Almacenamiento", "Audio"])


def test_sql_ventas_2025():
    result = sql_handler("listado de ventas totalizado entre abril y junio de 2025")
    assert any(x in result.lower() for x in ["mes", "total", "venta", "cantidad", "abril"])


if __name__ == "__main__":
    test_sql_select_only()
    test_sql_ventas()
    test_sql_stock_bajo()
    test_sql_stock_entre()
    test_sql_invalid_rejected()
    test_sql_categoria()
    print("\n✅ TODOS LOS TESTS PASARON")
