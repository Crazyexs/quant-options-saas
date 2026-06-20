from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from billing.models import Payment, Plan

User = get_user_model()


class BillingTests(TestCase):
    def test_approve_upgrades_and_extends(self):
        user = User.objects.create_user(email="p@b.com", password="x12345678")
        plan = Plan.objects.create(code="pro_monthly", name="Pro", tier="pro",
                                   price_thb=590, duration_days=30)
        pay = Payment.objects.create(user=user, plan=plan, amount=590,
                                     slip="slips/test.png")

        pay.approve()
        user.refresh_from_db()

        self.assertEqual(user.tier, "pro")
        self.assertTrue(user.has_tier("pro"))
        self.assertIsNotNone(user.subscription_until)
        self.assertGreater(user.subscription_until, timezone.now())
        self.assertEqual(pay.status, Payment.Status.APPROVED)

    def test_expired_subscription_downgrades_effective_tier(self):
        user = User.objects.create_user(email="x@b.com", password="x12345678")
        user.tier = "pro"
        user.subscription_until = timezone.now() - timezone.timedelta(days=1)
        user.save()
        self.assertEqual(user.effective_tier, "free")
