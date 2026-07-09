from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from flask import Flask, render_template, request, redirect, session, flash, url_for, Response
import csv
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "cloudstock_secret_key_2026"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "inventory.db")


# ==========================
# DATABASE CONNECTION
# ==========================
def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


# ==========================
# LOGIN
# ==========================
@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if username == "admin" and password == "admin123":

            session["logged_in"] = True
            session["username"] = username

            return redirect(url_for("dashboard"))

        flash("Invalid username or password!", "danger")

    return render_template("login.html")


# ==========================
# DASHBOARD
# ==========================
@app.route("/dashboard")
def dashboard():

    if "logged_in" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM products")
    total_products = cursor.fetchone()[0]

    cursor.execute("SELECT COALESCE(SUM(quantity),0) FROM products")
    total_stock = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM products WHERE quantity > 10")
    available_products = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM products WHERE quantity <= 10")
    low_stock = cursor.fetchone()[0]

    cursor.execute("SELECT * FROM products")
    rows = cursor.fetchall()

    # Low Stock Alert
    LOW_STOCK_LIMIT = 10

    low_stock_products = [
        row for row in rows
        if row["quantity"] < LOW_STOCK_LIMIT
    ]

    low_stock_count = len(low_stock_products)

    product_names = []
    product_quantities = []

    inventory_value = 0

    for row in rows:
        product_names.append(row["name"])
        product_quantities.append(row["quantity"])

        price = row["price"] if row["price"] else 0
        inventory_value += row["quantity"] * price

    conn.close()

    return render_template(
        "dashboard.html",
        total_products=total_products,
        total_stock=total_stock,
        available_products=available_products,
        low_stock=low_stock,
        inventory_value=inventory_value,
        product_names=product_names,
        product_quantities=product_quantities,
        low_stock_products=low_stock_products,
        low_stock_count=low_stock_count,
    )
# ==========================
# PRODUCTS
# ==========================
@app.route("/products")
def products():

    if "logged_in" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor()

    search = request.args.get("search", "")

    cursor.execute("""
        SELECT *
        FROM products
        WHERE name LIKE ?
        ORDER BY id DESC
    """, ('%' + search + '%',))

    products = cursor.fetchall()

    conn.close()

    return render_template(
        "products.html",
        products=products,
        search=search
    )


# ==========================
# ADD PRODUCT
# ==========================
@app.route("/add", methods=["GET", "POST"])
def add_product():

    if "logged_in" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        name = request.form.get("name")
        quantity = int(request.form.get("quantity"))

        conn = get_connection()
        cursor = conn.cursor()

        # Check whether price/category columns exist
        cursor.execute("PRAGMA table_info(products)")
        columns = [c[1] for c in cursor.fetchall()]

        if "category" in columns and "price" in columns:

            category = request.form.get("category")
            price = float(request.form.get("price"))

            cursor.execute(
                """
                INSERT INTO products
                (name, category, quantity, price)
                VALUES (?, ?, ?, ?)
                """,
                (name, category, quantity, price)
            )

        else:

            cursor.execute(
                """
                INSERT INTO products
                (name, quantity)
                VALUES (?, ?)
                """,
                (name, quantity)
            )

        conn.commit()
        conn.close()

        flash("Product added successfully!", "success")

        return redirect(url_for("products"))

    return render_template("add_product.html")
# ==========================
# EDIT PRODUCT
# ==========================
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_product(id):

    if "logged_in" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(products)")
    columns = [c[1] for c in cursor.fetchall()]

    if request.method == "POST":

        name = request.form.get("name")
        quantity = int(request.form.get("quantity"))

        if "category" in columns and "price" in columns:

            category = request.form.get("category")
            price = float(request.form.get("price"))

            cursor.execute(
                """
                UPDATE products
                SET name=?, category=?, quantity=?, price=?
                WHERE id=?
                """,
                (name, category, quantity, price, id)
            )

        else:

            cursor.execute(
                """
                UPDATE products
                SET name=?, quantity=?
                WHERE id=?
                """,
                (name, quantity, id)
            )

        conn.commit()
        conn.close()

        flash("Product updated successfully!", "warning")

        return redirect(url_for("products"))

    cursor.execute("SELECT * FROM products WHERE id=?", (id,))
    product = cursor.fetchone()

    conn.close()

    return render_template(
        "edit_product.html",
        product=product
    )


# ==========================
# DELETE PRODUCT
# ==========================
@app.route("/delete/<int:id>")
def delete_product(id):

    if "logged_in" not in session:
        return redirect("/")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM products WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    flash("🗑️ Product deleted successfully!", "success")

    return redirect("/products")

# ==========================
# REPORTS
# ==========================
@app.route("/reports")
def reports():

    if "logged_in" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM products")
    total_products = cursor.fetchone()[0]

    cursor.execute("SELECT COALESCE(SUM(quantity),0) FROM products")
    total_stock = cursor.fetchone()[0]

    cursor.execute("""
        SELECT name, quantity
        FROM products
        ORDER BY quantity DESC
        LIMIT 1
    """)
    highest = cursor.fetchone()

    cursor.execute("""
        SELECT name, quantity
        FROM products
        ORDER BY quantity ASC
        LIMIT 1
    """)
    lowest = cursor.fetchone()

    inventory_value = 0

    cursor.execute("PRAGMA table_info(products)")
    columns = [c[1] for c in cursor.fetchall()]

    if "price" in columns:

        cursor.execute("""
            SELECT quantity, price
            FROM products
        """)

        for row in cursor.fetchall():
            inventory_value += (row["quantity"] or 0) * (row["price"] or 0)

    conn.close()

    return render_template(
        "reports.html",
        total_products=total_products,
        total_stock=total_stock,
        inventory_value=inventory_value,
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

    return redirect(url_for("login"))


# ==========================
# RUN APP
# ==========================
# ==========================
# EXPORT PRODUCTS TO CSV
# ==========================

@app.route("/export_csv")
def export_csv():

    if "logged_in" not in session:
        return redirect("/")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, category, quantity, price
        FROM products
    """)

    products = cursor.fetchall()
    conn.close()

    def generate():

        data = []

        data.append([
            "ID",
            "Product Name",
            "Category",
            "Quantity",
            "Price"
        ])

        for product in products:
            data.append(product)

        output = []

        for row in data:
            output.append(",".join(map(str, row)))

        return "\n".join(output)

    return Response(
        generate(),
        mimetype="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=products.csv"
        }
    )
# ==========================
# EXPORT PDF
# ==========================

@app.route("/export_pdf")
def export_pdf():

    if "logged_in" not in session:
        return redirect("/")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, category, quantity, price
        FROM products
    """)

    products = cursor.fetchall()
    conn.close()

    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph(
            "<b><font size=18>CloudStock Inventory Report</font></b>",
            styles["Title"]
        )
    )

    data = [
        ["ID", "Product", "Category", "Qty", "Price"]
    ]

    for product in products:
        data.append([
            product[0],
            product[1],
            product[2],
            product[3],
            f"₹ {product[4]}"
        ])

    table = Table(data)

    table.setStyle(TableStyle([

        ("BACKGROUND",(0,0),(-1,0),colors.darkblue),
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),

        ("GRID",(0,0),(-1,-1),1,colors.black),

        ("BACKGROUND",(0,1),(-1,-1),colors.beige),

        ("ALIGN",(0,0),(-1,-1),"CENTER"),

        ("BOTTOMPADDING",(0,0),(-1,0),12)

    ]))

    elements.append(table)

    doc.build(elements)

    pdf = buffer.getvalue()

    buffer.close()

    return Response(
        pdf,
        mimetype="application/pdf",
        headers={
            "Content-Disposition":
            "attachment; filename=Inventory_Report.pdf"
        }
    )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )