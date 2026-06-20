from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

User = get_user_model()


class AuthFlowTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_login_me(self):
        r = self.client.post("/api/auth/register/",
                             {"email": "a@b.com", "password": "supersecret1"}, format="json")
        self.assertEqual(r.status_code, 201)

        r = self.client.post("/api/auth/token/",
                             {"email": "a@b.com", "password": "supersecret1"}, format="json")
        self.assertEqual(r.status_code, 200)
        token = r.data["access"]

        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)
        r = self.client.get("/api/auth/me/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["effective_tier"], "free")

    def test_me_requires_auth(self):
        self.assertEqual(self.client.get("/api/auth/me/").status_code, 401)
