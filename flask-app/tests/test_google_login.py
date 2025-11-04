import unittest
from unittest.mock import patch, MagicMock
from flask import Flask, session, redirect
from client_labs.app import app
from client_labs.database import get_db_connection, init_db

class GoogleLoginTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config.from_object('config.TestingConfig')
        self.app.config.update({"SECRET_KEY": "test_secret"})
        self.client = self.app.test_client()

        with self.app.app_context():
            # Initialize the database and create the tables
            with get_db_connection() as client:
                client.execute("DROP TABLE IF EXISTS users")
                client.execute("DROP TABLE IF EXISTS logs")
            init_db()

    def tearDown(self):
        # Clean up the database file
        with self.app.app_context():
            get_db_connection().close()

    @patch('client_labs.app.oauth.google')
    def test_google_login_and_user_creation(self, mock_google):
        # Mock the Google OAuth flow
        mock_google.authorize_redirect.return_value = redirect('/login/google/callback')
        mock_google.authorize_access_token.return_value = {
            'id_token': 'mock_id_token'
        }
        mock_google.parse_id_token.return_value = {
            'sub': '12345',
            'email': 'test@example.com',
            'name': 'Test User'
        }

        # Simulate the login redirect
        response = self.client.get('/login/google')
        self.assertEqual(response.status_code, 302)

        # Simulate the callback from Google
        with self.client as c:
            response = c.get('/login/google/callback')
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.location, '/')

            # Check if the user is in the session
            self.assertIn('user_id', session)

        # Check if the user was created in the database
        with self.app.app_context():
            with get_db_connection() as client:
                result_set = client.execute("SELECT * FROM users WHERE email = ?", ('test@example.com',))
                user = result_set.rows[0] if result_set.rows else None
                self.assertIsNotNone(user)
                self.assertEqual(user[2], 'test@example.com')

if __name__ == '__main__':
    unittest.main()
