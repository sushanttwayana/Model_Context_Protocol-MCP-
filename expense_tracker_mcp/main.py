from fastmcp import FastMCP
import os
from dotenv import load_dotenv
import psycopg2
import psycopg2.extras
from db import get_db_connection, init_db

# Load environment variables from .env file
load_dotenv()

# Get the PostgreSQL connection string from .env
DATABASE_URL = os.getenv("DATABASE_URL")

mcp = FastMCP("ExpenseTracker")

## Initialize the database
init_db()

### ADD EXPENSE TOOL
@mcp.tool()
def add_expense(date, amount, category, subcategory="", note=""):
    '''Add a new expense entry to the database and at the end of the transaction return the expense id to the user'''
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO expenses(date, amount, category, subcategory, note) VALUES (%s, %s, %s, %s, %s) RETURNING id",
                (date, amount, category, subcategory, note)
            )
            expense_id = cur.fetchone()["id"]
            conn.commit()
            return {"status": "ok", "id": expense_id}

## LIST EXPENSES TOOL
@mcp.tool()
def list_expenses(start_date, end_date):
    '''List expense entries within an inclusive date range.'''
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, date, amount, category, subcategory, note
                FROM expenses
                WHERE date BETWEEN %s AND %s
                ORDER BY id ASC
                """,
                (start_date, end_date)
            )
            return cur.fetchall()


### SUMMARIZE EXPENSES TOOL
@mcp.tool()
def summarize(start_date, end_date, category=None):
    '''Summarize expenses by category within an inclusive date range.'''
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            query = """
                SELECT category, SUM(amount) AS total_amount
                FROM expenses
                WHERE date BETWEEN %s AND %s
            """
            params = [start_date, end_date]

            if category:
                query += " AND category = %s"
                params.append(category)

            query += " GROUP BY category ORDER BY category ASC"

            cur.execute(query, params)
            return cur.fetchall()

# read the categories.json file and return the categories as a json object
CATEGORIES_PATH = os.path.join(os.path.dirname(__file__), "categories.json")

@mcp.resource("expense://categories", mime_type="application/json")
def categories():
    # Read fresh each time so you can edit the file without restarting
    with open(CATEGORIES_PATH, "r", encoding="utf-8") as f:
        return f.read()


#### Edit expenses tools
@mcp.tool()
def edit_expense(expense_id: int, date=None, amount=None, category=None, subcategory=None, note=None):
    '''Edit an existing expense entry by ID, updating any provided fields.'''
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Build dynamic SQL update statement based on provided fields
            update_fields = []
            params = []

            if date is not None:
                update_fields.append("date = %s")
                params.append(date)
            if amount is not None:
                update_fields.append("amount = %s")
                params.append(amount)
            if category is not None:
                update_fields.append("category = %s")
                params.append(category)
            if subcategory is not None:
                update_fields.append("subcategory = %s")
                params.append(subcategory)
            if note is not None:
                update_fields.append("note = %s")
                params.append(note)
            
            if not update_fields:
                return {"status": "error", "message": "No fields provided to update"}

            params.append(expense_id)
            query = f"UPDATE expenses SET {', '.join(update_fields)} WHERE id = %s"
            cur.execute(query, params)
            if cur.rowcount == 0:
                return {"status": "error", "message": "Expense ID not found"}
            
            conn.commit()
            return {"status": "ok", "message": f"Expense {expense_id} updated"}


#### DELETE EXPENSE TOOLS
@mcp.tool()
def delete_expense(expense_id: int):
    '''Delete an expense entry by ID.'''
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM expenses WHERE id = %s", (expense_id,))
            if cur.rowcount == 0:
                return {"status": "error", "message": "Expense ID not found"}
            conn.commit()
            return {"status": "ok", "message": f"Expense {expense_id} deleted"}


if __name__ == "__main__":
    mcp.run()