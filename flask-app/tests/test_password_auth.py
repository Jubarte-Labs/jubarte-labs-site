import unittest
from unittest.mock import patch
from flask import Flask, session
from client_labs.app import app
from client_labs.database import get_db_connection, init_db
from werkzeug.security import generate_password_hash

class PasswordAuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config.from_object('config.TestingConfig')
        self.app.config.update({"SECRET_KEY": "test_secret"})
        self.client = self.app.test_client()

        with self.app.app_context():
            with get_db_connection() as client:
                client.execute("DROP TABLE IF EXISTS users")
                client.execute("DROP TABLE IF EXISTS logs")
            init_db()

    def tearDown(self):
        with self.app.app_context():
            with get_db_connection() as client:
                client.execute("DROP TABLE IF EXISTS users")
                client.execute("DROP TABLE IF EXISTS logs")

    def test_registration_and_login(self):
        # Test registration
        response = self.client.post('/register', data={
            'email': 'test@example.com',
            'password': 'password',
            'confirm_password': 'password'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)

        # Test login
        response = self.client.post('/login', data={
            'email': 'test@example.com',
            'password': 'password'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Dashboard', response.data)

if __name__ == '__main__':
    unittest.main()
