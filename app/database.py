import sqlite3

connection = sqlite3.connect("inventory.db")

cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS products(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    quantity INTEGER NOT NULL
)
""")

cursor.execute("SELECT COUNT(*) FROM products")

count = cursor.fetchone()[0]

if count == 0:
    cursor.execute("INSERT INTO products(name, quantity) VALUES('Laptop',25)")
    cursor.execute("INSERT INTO products(name, quantity) VALUES('Keyboard',60)")
    cursor.execute("INSERT INTO products(name, quantity) VALUES('Mouse',90)")

connection.commit()

connection.close()

print("Database Created Successfully")