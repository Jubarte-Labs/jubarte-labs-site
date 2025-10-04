import os
import sys
import libsql_client

def get_db_connection():
    """Establishes a connection to the Turso database with detailed logging."""
    print("--- [DB] Attempting to get database connection...")
    
    url = os.getenv("TURSO_DATABASE_URL")
    auth_token = os.getenv("TURSO_AUTH_TOKEN")

    print(f"--- [DB] Found URL: {url}")
    print(f"--- [DB] Auth token found: {'Yes' if auth_token else 'No'}")

    if not url or not auth_token:
        print("--- [DB] ERROR: URL or auth token is missing.", file=sys.stderr)
        raise ValueError("Both TURSO_DATABASE_URL and TURSO_AUTH_TOKEN must be set")

    try:
        print("--- [DB] Creating database client...")
        client = libsql_client.create_client(url=url, auth_token=auth_token)
        print("--- [DB] Database client created successfully.")
        return client
    except Exception as e:
        print(f"--- [DB] FAILED to create database client: {e}", file=sys.stderr)
        raise

def init_db():
    """Initializes the database with detailed logging."""
    print("--- [INIT] Initializing database...")
    client = None
    try:
        client = get_db_connection()
        print("--- [INIT] Client object received. About to execute CREATE TABLE query...")
        
        # This is the line that has been failing. We'll now know for sure if we get here.
        client.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                tool_name TEXT NOT NULL,
                input_data TEXT,
                output_data TEXT
            )
        """)
        
        print("--- [INIT] SUCCESS: Database table checked/created successfully.")
    except Exception as e:
        # This will catch the error and print it with our custom message
        print(f"--- [INIT] FAILED during database initialization: {e}", file=sys.stderr)
        raise
    finally:
        if client:
            print("--- [INIT] Closing database connection.")
            client.close()