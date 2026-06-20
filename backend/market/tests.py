from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


def _auth(client, user):
    token = RefreshToken.for_user(user).access_token
    client.credentials(HTTP_AUTHORIZATION="Bearer " + str(token))


class MarketGatingTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.free = User.objects.create_user(email="f@b.com", password="x12345678")

    @patch("market.services.gex_symbol", return_value={"symbol": "ES", "spot": 5000})
    def test_free_user_gets_es(self, _m):
        _auth(self.client, self.free)
        self.assertEqual(self.client.get("/api/gex/?symbol=ES").status_code, 200)

    def test_free_user_blocked_on_other_symbol(self):
        _auth(self.client, self.free)
        self.assertEqual(self.client.get("/api/gex/?symbol=NQ").status_code, 403)

    @patch("market.services.exposure", return_value={"symbol": "ES", "greek": "GEX"})
    def test_exposure_requires_pro(self, _m):
        _auth(self.client, self.free)
        self.assertEqual(self.client.get("/api/exposure/?symbol=ES&greek=GEX").status_code, 403)

        self.free.tier = "pro"
        self.free.subscription_until = timezone.now() + timezone.timedelta(days=1)
        self.free.save()
        self.assertEqual(self.client.get("/api/exposure/?symbol=ES&greek=GEX").status_code, 200)

    def test_endpoints_require_auth(self):
        self.assertEqual(self.client.get("/api/gex/?symbol=ES").status_code, 401)
