# Jubarte Labs Website

This repository contains the codebase for the Jubarte Labs website and client portal.

- **`main-site/`**: A static marketing and landing page.
- **`flask-app/`**: A containerized Flask application that serves a client portal with authentication and various tools.

## Quick Start (Docker)

This project is configured to run in a local development environment using Docker and Docker Compose.

### 1. Setup

For a complete, step-by-step guide on how to set up the environment, configure secrets, and initialize the database, please refer to the **[Agent & Developer Onboarding Guide](./AGENTS.md)**.

### 2. Running the Application

Once you have completed the setup in the onboarding guide, you can start the application with a single command:

```bash
docker-compose up --build
```

The client portal will be available at `http://localhost:5000`.

### 3. Stopping the Application

```bash
docker-compose down
```