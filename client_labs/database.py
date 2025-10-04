import os
import libsql_client

def get_db_connection():
    """Establishes a connection to the Turso database."""
    url = os.getenv("TURSO_DATABASE_URL")
    auth_token = os.getenv("TURSO_AUTH_TOKEN")
    if not url:
        url = os.getenv("TURSO_DATABASE_URL")
        auth_token = os.getenv("TURSO_AUTH_TOKEN")
    if not url or not auth_token:
        raise ValueError("TURSO_DATABASE_URL and TURSO_AUTH_TOKEN environment variables must be set")
    return libsql_client.create_client_sync(url=url, auth_token=auth_token)
    return libsql_client.create_client_sync(url=url, auth_token=auth_token)

def init_db():
    """Initializes the database and creates the logs table if it doesn't exist."""
    with get_db_connection() as client:
        client.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                tool_name TEXT NOT NULL,
                input_data TEXT,
                output_data TEXT
            )
        """)