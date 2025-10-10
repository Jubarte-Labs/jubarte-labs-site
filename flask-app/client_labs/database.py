import os
import sys
import libsql_client
from sqlite3 import DatabaseError  # For database-specific exceptions

def get_db_connection():
    """Establishes a connection, handling both local file and remote DBs."""
    db_url = os.getenv("TURSO_DATABASE_URL")
    auth_token = os.getenv("TURSO_AUTH_TOKEN")

    if not db_url:
        raise ValueError("TURSO_DATABASE_URL must be set")

    # Handle local file-based database for testing/local dev
    if db_url.startswith("file:"):
        # Security check: Prevent path traversal attacks by checking for '..'
        file_path = db_url[5:]  # Remove 'file:' prefix
        if ".." in file_path:
            raise ValueError("Path traversal attempt detected in TURSO_DATABASE_URL")
        
        return libsql_client.create_client_sync(url=db_url)

    # Handle remote Turso database
    if not auth_token:
        raise ValueError("TURSO_AUTH_TOKEN must be set for remote databases")

    try:
        # Convert libsql:// URL to https:// for direct HTTP connection
        hostname = db_url.split("://")[1]
        http_url = f"https://{hostname}"
        
        # Pass the NEW https_url to the client
        client = libsql_client.create_client_sync(url=http_url, auth_token=auth_token)
        return client
    except Exception as e:
        raise

def init_db():
    """Initializes the database and creates required tables."""
    client = None
    try:
        client = get_db_connection()
        client.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                tool_name TEXT NOT NULL,
                input_data TEXT,
                output_data TEXT
            )
        """)
    except Exception as e:
        raise
    finally:
        if client:
            client.close()