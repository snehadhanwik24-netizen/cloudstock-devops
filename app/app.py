from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

DB_NAME = "inventory.db"

@app.route("/")
def login():
    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM products")
    total_products = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(quantity) FROM products")
    total_stock = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "dashboard.html",
        total_products=total_products,
        total_stock=total_stock
    )


@app.route("/products")
def products():

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    conn.close()

    return render_template("products.html", products=products)


@app.route("/add", methods=["GET", "POST"])
def add_product():

    if request.method == "POST":

        name = request.form["name"]
        quantity = request.form["quantity"]

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO products(name, quantity) VALUES (?, ?)",
            (name, quantity)
        )

        conn.commit()
        conn.close()

        return redirect("/products")

    return render_template("add_product.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)