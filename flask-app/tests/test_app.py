import pytest
from client_labs.app import app
from client_labs.database import init_db, get_db_connection

@pytest.fixture
def client():
    app.config.update({
        "TESTING": True,
        "SECRET_KEY": "test_secret",
        "WTF_CSRF_ENABLED": False,
    })
    with app.test_client() as client:
        with app.app_context():
            with get_db_connection() as db_client:
                db_client.execute("DROP TABLE IF EXISTS users")
                db_client.execute("DROP TABLE IF EXISTS logs")
            init_db()
            with get_db_connection() as db_client:
                db_client.execute(
                    "INSERT INTO users (id, email, name) VALUES (?, ?, ?)",
                    (1, "test@example.com", "Test User")
                )
        yield client

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

def test_tool_1_authenticated(client):
    """Test the word count tool functionality for an authenticated user."""

    with client.session_transaction() as sess:
        sess['user_id'] = 1

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

def test_sitemap_tool_access(client):
    """Test that the sitemap tool page is accessible to an authenticated user."""

    with client.session_transaction() as sess:
        sess['user_id'] = 1

    # Test GET request to the sitemap tool page
    rv = client.get('/tools/sitemap-processor')
    assert rv.status_code == 200
    assert b"Sitemap Processor" in rv.data