# Jubarte Labs Website

This repository contains two main components:
1.  **`main-site/`**: The static marketing website (deployed via Netlify).
2.  **`flask-app/`**: A Python Flask application (deployed via Render) that hosts various client tools.

---

## 🐳 Flask Application Setup (`flask-app/`)

This application uses a monolithic Flask structure with a Turso/SQLite database for logging.

### Prerequisites

*   Python 3.10+
*   `pip` and `venv`

### 1. Environment Variables

The application requires the following environment variables to be set in a `.env` file inside the `flask-app/` directory.

| Variable | Description | Required |
| :--- | :--- | :--- |
| `FLASK_SECRET_KEY` | A long, random string for session security. | **Yes** |
| `APP_USERNAME` | Username for the protected client login. | **Yes** |
| `APP_PASSWORD` | Password for the protected client login. | **Yes** |
| `TURSO_DATABASE_URL` | URL for the Turso database (e.g., `libsql://...`). | **Yes** |
| `TURSO_AUTH_TOKEN` | Authentication token for the Turso database. | **Yes** |

### 2. Installation

Navigate to the `flask-app` directory and install dependencies:

```bash
cd flask-app
python -m venv .venv
source .venv/bin/activate  # Use .venv\Scripts\activate on Windows
pip install -r requirements.txt -r requirements-local.txt
```

### 3. Running the Application

The application can be run directly:

```bash
python client_labs/app.py
```

### 4. Running Tests

Tests are configured to run without a live database connection using mocking.

```bash
cd flask-app
# Ensure you are in the virtual environment
set PYTHONPATH=. && python -m pytest tests
```

---

## 🌐 Main Site (`main-site/`)

This is a static site. Refer to the `main-site/package.json` for build instructions.

### Deployment

*   **Netlify:** Deploys the `main-site/` directory.
*   **Render:** Deploys the `flask-app/` directory using `gunicorn`.
