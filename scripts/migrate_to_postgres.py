import sqlite3
import psycopg2

PG = dict(
    host="postgres",
    port=5432,
    user="superagente",
    password="superagente",
    dbname="superagente",
)

SQLITE = "data/demo.db"

def migrate():
    sq = sqlite3.connect(SQLITE)
    sq.row_factory = sqlite3.Row

    pg = psycopg2.connect(**PG)
    pg.autocommit = True
    cur = pg.cursor()

    cur.execute("DROP TABLE IF EXISTS ventas")
    cur.execute("DROP TABLE IF EXISTS productos")

    cur.execute("""
        CREATE TABLE productos (
            id SERIAL PRIMARY KEY,
            nombre TEXT NOT NULL,
            categoria TEXT NOT NULL,
            precio REAL NOT NULL,
            stock INTEGER NOT NULL,
            stock_minimo INTEGER
        )
    """)
    cur.execute("""
        CREATE TABLE ventas (
            id SERIAL PRIMARY KEY,
            producto_id INTEGER NOT NULL REFERENCES productos(id),
            cantidad INTEGER NOT NULL,
            total REAL NOT NULL,
            fecha DATE NOT NULL,
            mes INTEGER
        )
    """)

    for row in sq.execute("SELECT * FROM productos ORDER BY id"):
        cur.execute(
            "INSERT INTO productos (id, nombre, categoria, precio, stock, stock_minimo) VALUES (%s, %s, %s, %s, %s, %s)",
            (row["id"], row["nombre"], row["categoria"], row["precio"], row["stock"], row["stock_minimo"]),
        )

    for row in sq.execute("SELECT * FROM ventas ORDER BY id"):
        cur.execute(
            "INSERT INTO ventas (id, producto_id, cantidad, total, fecha, mes) VALUES (%s, %s, %s, %s, %s, %s)",
            (row["id"], row["producto_id"], row["cantidad"], row["total"], row["fecha"], row["mes"]),
        )

    cur.execute("SELECT setval('productos_id_seq', (SELECT MAX(id) FROM productos))")
    cur.execute("SELECT setval('ventas_id_seq', (SELECT MAX(id) FROM ventas))")

    cur.close()
    pg.close()
    sq.close()
    print("Migración completada: datos copiados a PostgreSQL")

if __name__ == "__main__":
    migrate()
