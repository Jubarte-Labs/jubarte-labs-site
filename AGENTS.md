# Agent & Developer Onboarding Guide

This document provides a complete guide to setting up and running the Jubarte Labs web application in a local development environment using Docker.

## 1. Prerequisites

- **Docker**: Ensure Docker is installed and running on your system.
- **Docker Compose**: This is included with most Docker Desktop installations.

## 2. Environment Setup

The application uses a `.env` file to manage all necessary secrets and configuration variables.

### Step 2.1: Create the `.env` file

In the root directory of the project, create a new file named `.env`.

### Step 2.2: Populate the `.env` file

Copy the following content into your new `.env` file and fill in the values according to the instructions below.

```
FLASK_SECRET_KEY=
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
TURSO_DATABASE_URL=
TURSO_AUTH_TOKEN=
```

### Step 2.3: Variable Instructions

- `FLASK_SECRET_KEY`: A long, random string used for session security. You can generate one using Python: `python -c 'import secrets; print(secrets.token_hex(24))'`.
- `GOOGLE_CLIENT_ID` & `GOOGLE_CLIENT_SECRET`: These are obtained from the [Google API Console](https://console.developers.google.com/).
  - Create an "OAuth 2.0 Client ID" for a "Web application".
  - **Authorized JavaScript origins**: `http://localhost:5000`
  - **Authorized redirect URIs**: `http://localhost:5000/login/google/callback`
- `TURSO_DATABASE_URL` & `TURSO_AUTH_TOKEN`: These are obtained from your Turso dashboard.
  - **IMPORTANT**: For local development, create a dedicated "development" database (e.g., `jubarte-dev`) in Turso. **Do not use production credentials.** Use the URL and Auth Token from this new development database.

## 3. Running the Application

### Step 3.1: Build and Start the Container

Open a terminal in the root of the project and run:

```bash
docker-compose up --build
```

This command builds the Docker image for the Flask application, installs all Python dependencies, and starts the container. The web application will be accessible at `http://localhost:5000`.

### Step 3.2: Initialize the Database

For a first-time setup or when using a new, empty database, you must initialize the database schema.

With the container running, open a **second terminal** and run the following command:

```bash
docker-compose exec web flask init-db
```

This executes the `init-db` command inside the running container, creating the `users` and `logs` tables in your Turso development database.

## 4. Accessing the Application

- **Web Application**: `http://localhost:5000`
- **Login**: The application uses a protected-route model. You will be redirected to the login page, where you can register with an email/password or use the Google login you configured.

## 5. Stopping the Application

To stop the container, press `Ctrl+C` in the terminal where `docker-compose up` is running, or run the following command from the project root:

```bash
docker-compose down
```
