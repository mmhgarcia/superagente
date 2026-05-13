import sys
sys.path.insert(0, ".")

from agent.sql_tools import list_tables, get_schema, check_query, execute_query, build_schema_context


def test_list_tables():
    tables = list_tables()
    assert "productos" in tables
    assert "ventas" in tables


def test_get_schema_productos():
    schema = get_schema("productos")
    assert "productos" in schema
    assert "nombre" in schema
    assert "precio" in schema
    assert "stock" in schema


def test_get_schema_all():
    schema = get_schema()
    assert "productos" in schema
    assert "ventas" in schema


def test_check_query_valid():
    assert check_query("SELECT 1") is None


def test_check_query_invalid():
    err = check_query("SELECTX 1")
    assert err is not None


def test_execute_query():
    rows = execute_query("SELECT COUNT(*) as c FROM productos")
    assert isinstance(rows, list)
    assert rows[0]["c"] == 8


def test_execute_query_limit():
    rows = execute_query("SELECT * FROM ventas", limit=3)
    assert len(rows) <= 3


def test_execute_query_rejects_write():
    result = execute_query("DELETE FROM productos")
    assert "Error" in str(result)


def test_build_schema_context():
    ctx = build_schema_context()
    assert "productos" in ctx
    assert "ventas" in ctx
    assert "SELECT" in ctx


if __name__ == "__main__":
    test_list_tables()
    test_get_schema_productos()
    test_get_schema_all()
    test_check_query_valid()
    test_check_query_invalid()
    test_execute_query()
    test_execute_query_limit()
    test_execute_query_rejects_write()
    test_build_schema_context()
    print("\n✅ TODOS LOS TESTS DE SQL TOOLS PASARON")
