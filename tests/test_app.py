import pytest
from client_labs.app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_dashboard(client):
    """Test that the dashboard page loads."""
    rv = client.get('/')
    assert rv.status_code == 200
    assert b"Dashboard" in rv.data
    assert b"Welcome to your client portal." in rv.data