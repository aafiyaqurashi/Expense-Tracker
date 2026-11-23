
from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import date
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)

def get_db():
    conn = sqlite3.connect(os.path.join(BASE_DIR, "expenses.db"))
    conn.row_factory = sqlite3.Row
    return conn

# Create database
with get_db() as conn:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL
        )
    """)

# Home page
@app.route("/")
def index():
    conn = get_db()

    expenses = conn.execute(
        "SELECT * FROM expenses ORDER BY date DESC, id DESC"
    ).fetchall()

    total = conn.execute(
        "SELECT SUM(amount) FROM expenses"
    ).fetchone()[0] or 0

    current_month = date.today().strftime("%Y-%m")

    monthly_total = conn.execute(
        """
        SELECT SUM(amount) FROM expenses
        WHERE strftime('%Y-%m', date) = ?
        """,
        (current_month,)
    ).fetchone()[0] or 0

    category_totals = conn.execute(
        """
        SELECT category, SUM(amount) AS amount
        FROM expenses
        WHERE strftime('%Y-%m', date) = ?
        GROUP BY category
        ORDER BY amount DESC
        """,
        (current_month,)
    ).fetchall()

    conn.close()

    return render_template(
        "index.html",
        expenses=expenses,
        total=total,
        monthly_total=monthly_total,
        category_totals=category_totals
    )

# Add expense
@app.route("/add", methods=["POST"])
def add():
    title = request.form["title"]
    amount = request.form["amount"]
    category = request.form["category"]
    expense_date = request.form["date"]

    conn = get_db()
    conn.execute(
        """
        INSERT INTO expenses (title, amount, category, date)
        VALUES (?, ?, ?, ?)
        """,
        (title, amount, category, expense_date)
    )
    conn.commit()
    conn.close()

    return redirect("/")

# Delete expense
@app.route("/delete/<int:id>")
def delete(id):
    conn = get_db()
    conn.execute(
        "DELETE FROM expenses WHERE id = ?",
        (id,)
    )
    conn.commit()
    conn.close()

    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
