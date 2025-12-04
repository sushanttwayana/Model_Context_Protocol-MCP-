from fastmcp import FastMCP
import os
from dotenv import load_dotenv
import psycopg2
import psycopg2.extras
from db import get_db_connection, init_db
import asyncio
import asyncpg

# Load environment variables from .env file
load_dotenv()

# Get the PostgreSQL connection string from .env
DATABASE_URL = os.getenv("DATABASE_URL")

mcp = FastMCP("ExpenseTracker")

# Global connection pool
db_pool: asyncpg.Pool = None

## Initialize the database
async def get_db_pool() -> asyncpg.Pool:
    """Get the shared asyncpg connection pool."""
    global db_pool
    if db_pool is None:
        raise RuntimeError("Database pool not initialized")
    return db_pool

async def init_pool():
    """Initialize the asyncpg connection pool."""
    global db_pool
    db_pool = await asyncpg.create_pool(
        DATABASE_URL,
        min_size=5,
        max_size=20,
        command_timeout=60
    )
    print("✅ Async database pool initialized")

### ADD EXPENSE TOOL (Async)
@mcp.tool()
async def add_expense(date, amount, category, subcategory="", note=""):
    '''Add a new expense entry to the database and return the expense id.'''
    async with get_db_pool().acquire() as conn:
        expense_id = await conn.fetchval(
            """
            INSERT INTO expenses(date, amount, category, subcategory, note) 
            VALUES ($1, $2, $3, $4, $5) 
            RETURNING id
            """,
            date, amount, category, subcategory, note
        )
        return {"status": "ok", "id": expense_id}

### LIST EXPENSES TOOL (Async)
@mcp.tool()
async def list_expenses(start_date, end_date):
    '''List expense entries within an inclusive date range.'''
    async with get_db_pool().acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT id, date, amount, category, subcategory, note
            FROM expenses
            WHERE date BETWEEN $1 AND $2
            ORDER BY id ASC
            """,
            start_date, end_date
        )
        # Convert Record objects to dicts (asyncpg equivalent of RealDictCursor)
        return [{"id": r["id"], "date": r["date"], "amount": r["amount"], 
                "category": r["category"], "subcategory": r["subcategory"], 
                "note": r["note"]} for r in rows]

### SUMMARIZE EXPENSES TOOL (Async)
@mcp.tool()
async def summarize(start_date, end_date, category=None):
    '''Summarize expenses by category within an inclusive date range.'''
    async with get_db_pool().acquire() as conn:
        query = """
            SELECT category, SUM(amount) AS total_amount
            FROM expenses
            WHERE date BETWEEN $1 AND $2
        """
        params = [start_date, end_date]
        
        if category:
            query += " AND category = $3"
            params.append(category)
        
        query += " GROUP BY category ORDER BY category ASC"
        
        rows = await conn.fetch(query, *params)
        return [{"category": r["category"], "total_amount": float(r["total_amount"])} for r in rows]

# Resource stays sync (file I/O)
CATEGORIES_PATH = os.path.join(os.path.dirname(__file__), "categories.json")

@mcp.resource("expense://categories", mime_type="application/json")
def categories():
    with open(CATEGORIES_PATH, "r", encoding="utf-8") as f:
        return f.read()

### EDIT EXPENSE TOOL (Async)
@mcp.tool()
async def edit_expense(expense_id: int, date=None, amount=None, category=None, subcategory=None, note=None):
    '''Edit an existing expense entry by ID, updating provided fields.'''
    async with get_db_pool().acquire() as conn:
        async with conn.transaction():
            update_fields = []
            params = []
            
            if date is not None:
                update_fields.append("date = $" + str(len(params) + 1))
                params.append(date)
            if amount is not None:
                update_fields.append("amount = $" + str(len(params) + 1))
                params.append(amount)
            if category is not None:
                update_fields.append("category = $" + str(len(params) + 1))
                params.append(category)
            if subcategory is not None:
                update_fields.append("subcategory = $" + str(len(params) + 1))
                params.append(subcategory)
            if note is not None:
                update_fields.append("note = $" + str(len(params) + 1))
                params.append(note)
            
            if not update_fields:
                return {"status": "error", "message": "No fields provided to update"}
            
            params.append(expense_id)
            query = f"UPDATE expenses SET {', '.join(update_fields)} WHERE id = ${len(params)}"
            
            result = await conn.execute(query, *params)
            if result == "UPDATE 0":
                return {"status": "error", "message": "Expense ID not found"}
            
            return {"status": "ok", "message": f"Expense {expense_id} updated"}

### DELETE EXPENSE TOOL (Async)
@mcp.tool()
async def delete_expense(expense_id: int):
    '''Delete an expense entry by ID.'''
    async with get_db_pool().acquire() as conn:
        async with conn.transaction():
            result = await conn.execute("DELETE FROM expenses WHERE id = $1", expense_id)
            if result == "DELETE 0":
                return {"status": "error", "message": "Expense ID not found"}
            return {"status": "ok", "message": f"Expense {expense_id} deleted"}

### CREDIT EXPENSE TOOL (Async)
@mcp.tool()
async def credit_salary(amount: float, source: str = "salary"):
    '''Add credit amount to the available total from salary or other sources.'''
    async with get_db_pool().acquire() as conn:
        async with conn.transaction():
            # Update balance
            await conn.execute("UPDATE balance SET total = total + $1 WHERE id = 1", amount)
            # Log as income expense
            await conn.execute(
                """
                INSERT INTO expenses(date, amount, category, note) 
                VALUES (CURRENT_DATE, $1, $2, $3)
                """,
                amount, f"income:{source}", f"Credit from {source}"
            )
            # Get updated total
            total = await conn.fetchval("SELECT total FROM balance WHERE id=1")
            return {"status": "ok", "total_balance": float(total)}

### SET SPECIFIC BUDGET FOR A CATEGORY TOOL (Async)
@mcp.tool()
async def set_budget(category: str, amount: float):
    '''Set budget limit for a specific category.'''
    async with get_db_pool().acquire() as conn:
        async with conn.transaction():
            await conn.execute("""
                INSERT INTO budgets (category, amount) VALUES ($1, $2)
                ON CONFLICT (category) DO UPDATE SET amount = EXCLUDED.amount
            """, category, amount)
            return {"status": "ok", "category": category, "budget": amount}

### CHECK BUDGET STATUS TOOL (Async)
@mcp.tool()
async def check_budget_status(category: str):
    '''Return spent and remaining amount for a budgeted category.'''
    async with get_db_pool().acquire() as conn:
        # Get budget
        budget = await conn.fetchval("SELECT amount FROM budgets WHERE category = $1", category)
        if budget is None:
            return {"status": "error", "message": f"No budget set for category {category}"}
        
        # Calculate total spent
        spent = await conn.fetchval("""
            SELECT COALESCE(SUM(amount), 0) AS spent FROM expenses WHERE category = $1
        """, category)
        
        remaining = float(budget) - float(spent)
        notification = (
            "You have exceeded your budget!" if remaining < 0 
            else f"You are within your budget. Remaining: {remaining:.2f}"
        )
        
        return {
            "status": "ok",
            "category": category,
            "budget": float(budget),
            "spent": float(spent),
            "remaining": remaining,
            "notification": notification,
        }

### FINANCIAL SUMMARY TOOL (Async)
@mcp.tool()
async def financial_summary():
    """Return a summary of the financial situation including total balance, total spent, budgets, and remaining balance."""
    async with get_db_pool().acquire() as conn:
        # Get balance
        total_balance = await conn.fetchval("SELECT total FROM balance WHERE id = 1")
        total_balance = float(total_balance) if total_balance is not None else 0.0
        
        # Total spent
        total_spent = await conn.fetchval("SELECT COALESCE(SUM(amount), 0) AS total_spent FROM expenses")
        total_spent = float(total_spent) if total_spent is not None else 0.0
        
        # Budgets
        budget_rows = await conn.fetch("SELECT category, amount FROM budgets ORDER BY category ASC")
        budgets = [
            {"category": r["category"], "budget": float(r["amount"])}
            for r in budget_rows
        ]
        
        remaining_balance = total_balance - total_spent
        
        return {
            "status": "ok",
            "total_balance": total_balance,
            "total_spent": total_spent,
            "remaining_balance": remaining_balance,
            "budgets": budgets,
        }

async def main():
    """Main async entrypoint."""
    # Sync DB init first (tables must exist)
    try:
        init_db()
    except Exception as e:
        print("Failed to initialize database:", e)
    
    # Initialize async pool
    await init_pool()
    
    try:
        # Run FastMCP async server
        await mcp.run_async(transport="http", port=8000)
    finally:
        if db_pool:
            await db_pool.close()
            print("✅ Database pool closed")


### new tools addeed
# some changes on this branch

if __name__ == "__main__":
    asyncio.run(main())
