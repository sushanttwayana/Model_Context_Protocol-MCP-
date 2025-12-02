import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    """Return a new DB connection with RealDictCursor"""
    return psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)

def init_db():
    """Initialize all required tables"""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Expenses table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS expenses(
                    id SERIAL PRIMARY KEY,
                    date DATE NOT NULL,
                    amount NUMERIC NOT NULL,
                    category TEXT NOT NULL,
                    subcategory TEXT DEFAULT '',
                    note TEXT DEFAULT ''
                )
            """)

            # Balance table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS total_available_balance (
                    id SERIAL PRIMARY KEY,
                    total NUMERIC NOT NULL DEFAULT 0
                )
            """)

            # Insert initial row with 0 if empty
            cur.execute("""
                INSERT INTO total_available_balance (total)
                SELECT 0 WHERE NOT EXISTS (SELECT 1 FROM total_available_balance)
            """)

            # Budgets table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS budgets(
                    id SERIAL PRIMARY KEY,
                    category TEXT UNIQUE NOT NULL,
                    amount NUMERIC NOT NULL
                )
            """)

            conn.commit()
