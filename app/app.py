from flask import Flask, render_template, request, redirect, session, flash, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = "cloudstock_secret_key_2026"

DB_NAME = "inventory.db"


# ==========================
# LOGIN
# ==========================
@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin123":

            session["logged_in"] = True
            session["username"] = username

            return redirect("/dashboard")

        else:

            flash("Invalid username or password!", "danger")
            return redirect("/")

    return render_template("login.html")


# ==========================
# DASHBOARD
# ==========================
@app.route("/dashboard")
def dashboard():

    if "logged_in" not in session:
        return redirect("/")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM products")
    total_products = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(quantity) FROM products")
    total_stock = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM products WHERE quantity > 10")
    available_products = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM products WHERE quantity <= 10")
    low_stock = cursor.fetchone()[0]

    cursor.execute("SELECT name, quantity FROM products")
    chart_data = cursor.fetchall()

    product_names = [row[0] for row in chart_data]
    product_quantities = [row[1] for row in chart_data]

    conn.close()

    return render_template(
        "dashboard.html",
        total_products=total_products,
        total_stock=total_stock,
        available_products=available_products,
        low_stock=low_stock,
        product_names=product_names,
        product_quantities=product_quantities
    )


# ==========================
# PRODUCTS
# ==========================
@app.route("/products")
def products():

    if "logged_in" not in session:
        return redirect("/")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    conn.close()

    return render_template("products.html", products=products)


# ==========================
# ADD PRODUCT
# ==========================
@app.route("/add", methods=["GET", "POST"])
def add_product():

    if "logged_in" not in session:
        return redirect("/")

    if request.method == "POST":

        name = request.form["name"]
category = request.form["category"]
quantity = int(request.form["quantity"])
price = float(request.form["price"])
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

      cursor.execute(
    """
    INSERT INTO products
    (name, category, quantity, price)
    VALUES (?, ?, ?, ?)
    """,
    (name, category, quantity, price)
)

        conn.commit()
        conn.close()

        flash("✅ Product added successfully!", "success")

        return redirect("/products")

    return render_template("add_product.html")


# ==========================
# EDIT PRODUCT
# ==========================
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_product(id):

    if "logged_in" not in session:
        return redirect("/")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    if request.method == "POST":

        name = request.form["name"]
        quantity = request.form["quantity"]

        cursor.execute(
            "UPDATE products SET name=?, quantity=? WHERE id=?",
            (name, quantity, id)
        )

        conn.commit()
        conn.close()

        flash("✏️ Product updated successfully!", "warning")

        return redirect("/products")

    cursor.execute("SELECT * FROM products WHERE id=?", (id,))
    product = cursor.fetchone()

    conn.close()

    return render_template("edit_product.html", product=product)


# ==========================
# DELETE PRODUCT
# ==========================
@app.route("/delete/<int:id>")
def delete_product(id):

    if "logged_in" not in session:
        return redirect("/")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM products WHERE id=?", (id,))

    conn.commit()
    conn.close()

    flash("🗑️ Product deleted successfully!", "danger")

    return redirect(url_for("products"))


# ==========================
# REPORTS
# ==========================
@app.route("/reports")
def reports():

    if "logged_in" not in session:
        return redirect("/")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM products")
    total_products = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(quantity) FROM products")
    total_stock = cursor.fetchone()[0]

    cursor.execute("SELECT name, quantity FROM products ORDER BY quantity DESC LIMIT 1")
    highest = cursor.fetchone()

    cursor.execute("SELECT name, quantity FROM products ORDER BY quantity ASC LIMIT 1")
    lowest = cursor.fetchone()

    conn.close()

    return render_template(
        "reports.html",
        total_products=total_products,
        total_stock=total_stock,
        highest=highest,
        lowest=lowest
    )


# ==========================
# LOGOUT
# ==========================
@app.route("/logout")
def logout():

    session.clear()

    flash("Logged out successfully!", "info")

    return redirect("/")


# ==========================
# RUN APP
# ==========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)