from fastapi import FastAPI, Body
import os
from dotenv import load_dotenv
import psycopg2
import psycopg2.extras
from db import get_db_connection, init_db
from fastapi.responses import JSONResponse
import json  # For loading categories if needed, but since reading as string, not necessary

# Load environment variables from .env file
load_dotenv()

# Get the PostgreSQL connection string from .env
DATABASE_URL = os.getenv("DATABASE_URL")

app = FastAPI(title="Expense Tracker API")

# Initialize the database
init_db()

### ADD EXPENSE ENDPOINT
@app.post("/add_expense")
def add_expense(date: str = Body(...), amount: float = Body(...), category: str = Body(...), subcategory: str = Body(default=""), note: str = Body(default="")):
    '''Add a new expense entry to the database and return the expense id'''
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO expenses(date, amount, category, subcategory, note) VALUES (%s, %s, %s, %s, %s) RETURNING id",
                (date, amount, category, subcategory, note)
            )
            expense_id = cur.fetchone()["id"]
            conn.commit()
            return {"status": "ok", "id": expense_id}

### LIST EXPENSES ENDPOINT
@app.post("/list_expenses")
def list_expenses(start_date: str = Body(...), end_date: str = Body(...)):
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

### SUMMARIZE EXPENSES ENDPOINT
@app.post("/summarize")
def summarize(start_date: str = Body(...), end_date: str = Body(...), category: str | None = Body(default=None)):
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

# Path to categories.json
CATEGORIES_PATH = os.path.join(os.path.dirname(__file__), "categories.json")

@app.get("/categories", response_class=JSONResponse)
def get_categories():
    # Read fresh each time so you can edit the file without restarting
    with open(CATEGORIES_PATH, "r", encoding="utf-8") as f:
        content = f.read()
        return json.loads(content)  # Parse to JSON to return as JSON response

### EDIT EXPENSE ENDPOINT
@app.post("/edit_expense")
def edit_expense(expense_id: int = Body(...), date: str | None = Body(default=None), amount: float | None = Body(default=None), category: str | None = Body(default=None), subcategory: str | None = Body(default=None), note: str | None = Body(default=None)):
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

### DELETE EXPENSE ENDPOINT
@app.post("/delete_expense")
def delete_expense(expense_id: int = Body(...)):
    '''Delete an expense entry by ID.'''
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM expenses WHERE id = %s", (expense_id,))
            if cur.rowcount == 0:
                return {"status": "error", "message": "Expense ID not found"}
            conn.commit()
            return {"status": "ok", "message": f"Expense {expense_id} deleted"}

### CREDIT SALARY ENDPOINT
@app.post("/credit_salary")
def credit_salary(amount: float = Body(...), source: str = Body(default="salary")):
    '''Add credit amount to the available total from salary or other sources.'''
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE balance SET total = total + %s WHERE id = 1", (amount,))
            # Optionally log this as a positive "income" expense for record keeping
            cur.execute(
                "INSERT INTO expenses(date, amount, category, note) VALUES (CURRENT_DATE, %s, %s, %s)",
                (amount, f"income:{source}", f"Credit from {source}")
            )
            conn.commit()
            cur.execute("SELECT total FROM balance WHERE id=1")
            total = cur.fetchone()["total"]
            return {"status": "ok", "total_balance": total}

### SET BUDGET ENDPOINT
@app.post("/set_budget")
def set_budget(category: str = Body(...), amount: float = Body(...)):
    '''Set budget limit for a specific category.'''
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Insert or update budget for category
            cur.execute("""
                INSERT INTO budgets (category, amount) VALUES (%s, %s)
                ON CONFLICT (category) DO UPDATE SET amount = EXCLUDED.amount
            """, (category, amount))
            conn.commit()
            return {"status": "ok", "category": category, "budget": amount}

### CHECK BUDGET STATUS ENDPOINT
@app.post("/check_budget_status")
def check_budget_status(category: str = Body(...)):
    '''Return spent and remaining amount for a budgeted category.'''
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Get budget
            cur.execute("SELECT amount FROM budgets WHERE category = %s", (category,))
            budget_row = cur.fetchone()
            if not budget_row:
                return {"status": "error", "message": f"No budget set for category {category}"}

            budget = budget_row["amount"]
            # Calculate total spent on category (negative amount treated as expense)
            cur.execute("""
                SELECT COALESCE(SUM(amount), 0) AS spent FROM expenses WHERE category = %s
            """, (category,))
            spent = cur.fetchone()["spent"]
            remaining = budget - spent
            # Basic notification message
            notification = (
                "You have exceeded your budget!" if remaining < 0 else f"You are within your budget and your remaining balance is {remaining}."
            )
            return {
                "status": "ok",
                "category": category,
                "budget": budget,
                "spent": spent,
                "remaining": remaining,
                "notification": notification,
            }

### FINANCIAL SUMMARY ENDPOINT
@app.get("/financial_summary")
def financial_summary():
    '''Return a summary of the financial situation including total balance, total spent, budgets, and remaining balance.'''
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT total FROM balance WHERE id=1")
            total_balance = cur.fetchone()["total"]

            cur.execute("SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE amount < 0")
            total_spent = cur.fetchone()[0] or 0

            cur.execute("SELECT category, amount FROM budgets")
            budgets = cur.fetchall()

            # You can calculate remaining and spent per budget category here as well

            return {
                "total_balance": float(total_balance),
                "total_spent": float(total_spent),
                "budgets": budgets,
                "remaining_balance": float(total_balance) + float(total_spent),  # expenses negative
            }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)