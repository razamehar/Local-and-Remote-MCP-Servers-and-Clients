from db.db_init import init_db
from config.constants import mcp
import sqlite3
from config.constants import CATEGORIES_PATH, DB_PATH, mcp


@mcp.tool()
def add_expense(date, amount, category, subcategory="", note=""):
    """Add a new expense entry to the database."""
    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute(
            "INSERT INTO expenses(date, amount, category, subcategory, note) VALUES (?,?,?,?,?)",
            (date, amount, category, subcategory, note)
        )
        return {"status": "ok", "id": cur.lastrowid}


@mcp.tool()
def list_expenses(start_date, end_date):
    """List expense entries within an inclusive date range."""
    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute(
            """
            SELECT id, date, amount, category, subcategory, note
            FROM expenses
            WHERE date BETWEEN ? AND ?
            ORDER BY id ASC
            """,
            (start_date, end_date)
        )
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]


@mcp.tool()
def summarize(start_date, end_date, category=None):
    """Summarize expenses by category within an inclusive date range."""
    with sqlite3.connect(DB_PATH) as c:
        query = """
            SELECT category, SUM(amount) AS total_amount
            FROM expenses
            WHERE date BETWEEN ? AND ?
        """
        params = [start_date, end_date]

        if category:
            query += " AND category = ?"
            params.append(category)

        query += " GROUP BY category ORDER BY category ASC"

        cur = c.execute(query, params)
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]


@mcp.tool()
def edit_expense(expense_id, date=None, amount=None, category=None, subcategory=None, note=None):
    """Edit an existing expense entry. Only provided fields will be updated."""
    fields = {}
    if date is not None:
        fields["date"] = date
    if amount is not None:
        fields["amount"] = amount
    if category is not None:
        fields["category"] = category
    if subcategory is not None:
        fields["subcategory"] = subcategory
    if note is not None:
        fields["note"] = note

    if not fields:
        return {"status": "error", "message": "No fields to update"}

    set_clause = ", ".join(f"{k} = ?" for k in fields)
    params = list(fields.values()) + [expense_id]

    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute(f"UPDATE expenses SET {set_clause} WHERE id = ?", params)
        if cur.rowcount == 0:
            return {"status": "error", "message": "Expense not found"}
        return {"status": "ok", "updated_id": expense_id}


@mcp.tool()
def delete_by_category(category):
    """Delete all expenses under a specific category."""
    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute("DELETE FROM expenses WHERE category = ?", (category,))
        return {"status": "ok", "deleted_count": cur.rowcount}


@mcp.resource("expense://categories", mime_type="application/json")
def categories():
    # Read fresh each time so you can edit the file without restarting
    with open(CATEGORIES_PATH, "r", encoding="utf-8") as f:
        return f.read()


if __name__ == "__main__":
    init_db()
    mcp.run()
