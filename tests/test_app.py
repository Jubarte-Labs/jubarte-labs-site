import pytest
from client_labs.app import app

@pytest.fixture
def client():
    app.config.update({
        "TESTING": True,
        "SECRET_KEY": "test_secret",
        "WTF_CSRF_ENABLED": False
    })
    with app.test_client() as client:
        yield client

def test_unauthenticated_access_redirects_to_login(client):
    """Test that accessing protected pages redirects unauthenticated users to the login page."""
    response = client.get("/")
    assert response.status_code == 302
    assert "login" in response.location

    response = client.get("/protected")
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