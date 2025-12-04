import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():  # DEPRECATED - Keep only for backward compatibility
    """Sync connection - DEPRECATED for async tools"""
    print("⚠️  Using deprecated sync connection")
    try:
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)
        return conn
    except Exception as e:
        print(f"❌ Sync connection failed: {e}")
        raise

def init_db():
    """Initialize all required tables (SYNC - called once at startup)"""
    try:
        print("🔄 Initializing database tables (SYNC)...")
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
                print("✅ Expenses table created/verified")

                # Balance table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS balance (
                        id SERIAL PRIMARY KEY,
                        total NUMERIC NOT NULL DEFAULT 0
                    )
                """)
                print("✅ Balance table created/verified")

                # Insert initial row with 0 if empty
                cur.execute("""
                    INSERT INTO balance (total)
                    SELECT 0 WHERE NOT EXISTS (SELECT 1 FROM balance)
                """)
                print("✅ Initial balance row inserted (if needed)")

                # Budgets table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS budgets(
                        id SERIAL PRIMARY KEY,
                        category TEXT UNIQUE NOT NULL,
                        amount NUMERIC NOT NULL
                    )
                """)
                print("✅ Budgets table created/verified")

                conn.commit()
                print("✅ All database tables initialized successfully")
                
    except Exception as e:
        print(f"❌ init_db failed: {e}")
        import traceback
        traceback.print_exc()
        raise
