import sqlite3

connection = sqlite3.connect("inventory.db")

cursor = connection.cursor()

# Delete old table (only for development)
cursor.execute("DROP TABLE IF EXISTS products")

# Create new table
cursor.execute("""
CREATE TABLE products(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    price REAL NOT NULL
)
""")

# Sample Data
products = [

    ("Laptop", "Electronics", 25, 50000),

    ("Keyboard", "Accessories", 60, 1200),

    ("Mouse", "Accessories", 90, 800),

    ("Monitor", "Electronics", 15, 15000),

    ("Printer", "Office", 8, 18000)

]

cursor.executemany(

    "INSERT INTO products(name, category, quantity, price) VALUES (?, ?, ?, ?)",

    products

)

connection.commit()

connection.close()

print("✅ Database Created Successfully")