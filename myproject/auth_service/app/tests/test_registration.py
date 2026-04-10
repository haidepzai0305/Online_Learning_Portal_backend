import os
import django
import json
import unittest
from django.test import RequestFactory
from django.http import JsonResponse

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from myproject.auth_service.app.api.views import register_view

class TestRegistrationLogic(unittest.TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_missing_fields(self):
        # Test missing all fields
        request = self.factory.post('/api/auth/register/', data=json.dumps({}), content_type='application/json')
        response = register_view(request)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn("Missing required fields", data["error"])
        self.assertIn("email", data["error"])
        self.assertIn("username", data["error"])
        self.assertIn("password", data["error"])

    def test_invalid_json(self):
        # Test malformed JSON
        request = self.factory.post('/api/auth/register/', data="not-json", content_type='application/json')
        response = register_view(request)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertEqual(data["error"], "Invalid JSON format")

    def test_invalid_email(self):
        # Test invalid email format
        payload = {"email": "invalid-email", "username": "testuser", "password": "password123"}
        request = self.factory.post('/api/auth/register/', data=json.dumps(payload), content_type='application/json')
        response = register_view(request)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertEqual(data["error"], "Invalid email format")

    def test_short_password(self):
        # Test password too short
        payload = {"email": "test@example.com", "username": "testuser", "password": "123"}
        request = self.factory.post('/api/auth/register/', data=json.dumps(payload), content_type='application/json')
        response = register_view(request)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertEqual(data["error"], "Password must be at least 6 characters long")

if __name__ == "__main__":
    unittest.main()
