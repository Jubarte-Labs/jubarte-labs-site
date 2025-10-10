import pytest
from client_labs.app import create_app

@pytest.fixture
def app(monkeypatch):
    monkeypatch.setenv("TURSO_DATABASE_URL", "file:test.db")
    monkeypatch.setenv("FLASK_SECRET_KEY", "test_secret")
    app = create_app()
    app.config.update({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
    })
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

def test_unauthenticated_access_redirects_to_login(client):
    """Test that accessing protected pages redirects unauthenticated users to the login page."""
    response = client.get("/")
    assert response.status_code == 302
    assert "login" in response.location

    response = client.get("/protected")
    assert response.status_code == 302
    assert "login" in response.location

    response = client.get("/tool-1")
    assert response.status_code == 302
    assert "login" in response.location

def test_login_and_logout(client, monkeypatch):
    """Test the complete login and logout flow."""
    monkeypatch.setenv("APP_USERNAME", "testuser")
    monkeypatch.setenv("APP_PASSWORD", "testpass")

    # Test successful login and redirection
    response = client.post("/login", data={"username": "testuser", "password": "testpass"}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Dashboard" in response.data

    # Verify access to protected pages after login
    response = client.get("/")
    assert response.status_code == 200
    assert b"Dashboard" in response.data

    response = client.get("/protected")
    assert response.status_code == 200
    assert b"Protected Page" in response.data

    # Test logout
    response = client.get("/logout", follow_redirects=True)
    assert response.status_code == 200
    assert b"Login" in response.data

    # Verify that user is logged out and cannot access protected pages
    response = client.get("/")
    assert response.status_code == 302
    assert "login" in response.location

def test_invalid_login(client, monkeypatch):
    """Test that invalid login credentials display an error message."""
    monkeypatch.setenv("APP_USERNAME", "testuser")
    monkeypatch.setenv("APP_PASSWORD", "testpass")

    response = client.post("/login", data={"username": "wronguser", "password": "wrongpassword"}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Invalid credentials" in response.data
    assert b"Dashboard" not in response.data

def test_tool_1_authenticated(client, monkeypatch):
    """Test the word count tool functionality for an authenticated user."""
    monkeypatch.setenv("APP_USERNAME", "testuser")
    monkeypatch.setenv("APP_PASSWORD", "testpass")

    # Log in
    client.post("/login", data={"username": "testuser", "password": "testpass"}, follow_redirects=True)

    # Test GET request to the tool page
    rv = client.get('/tool-1')
    assert rv.status_code == 200
    assert b"Word Count Tool" in rv.data

    # Test POST request with word count data
    rv = client.post('/tool-1', data=dict(
        text_input="This is a test."
    ), follow_redirects=True)
    assert rv.status_code == 200
    assert b"The number of words is: 4" in rv.data

def test_sitemap_tool_access(client, monkeypatch):
    """Test that the sitemap tool page is accessible to an authenticated user."""
    monkeypatch.setenv("APP_USERNAME", "testuser")
    monkeypatch.setenv("APP_PASSWORD", "testpass")

    # Log in
    client.post("/login", data={"username": "testuser", "password": "testpass"}, follow_redirects=True)

    # Test GET request to the sitemap tool page
    rv = client.get('/tools/sitemap-processor')
    assert rv.status_code == 200
    assert b"Sitemap Processor" in rv.data