import os
import sys
import libsql_client
from sqlite3 import DatabaseError  # For database-specific exceptions

def get_db_connection():
    """Establishes a connection, forcing HTTPS instead of WebSockets."""
    db_url = os.getenv("TURSO_DATABASE_URL")
    auth_token = os.getenv("TURSO_AUTH_TOKEN")

    if not db_url or not auth_token:
        raise ValueError("Both TURSO_DATABASE_URL and TURSO_AUTH_TOKEN must be set")

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