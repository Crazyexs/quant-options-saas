from django.conf import settings
from django.db import models
from django.utils import timezone

from accounts.models import Tier


class Plan(models.Model):
    code = models.CharField(max_length=32, unique=True)      # e.g. "pro_monthly"
    name = models.CharField(max_length=80)
    tier = models.CharField(max_length=10, choices=Tier.choices, default=Tier.PRO)
    price_thb = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.PositiveIntegerField(default=30)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.price_thb} THB / {self.duration_days}d)"


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name="payments")
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT)
    slip = models.ImageField(upload_to="slips/%Y/%m/")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                    on_delete=models.SET_NULL, related_name="reviewed_payments")

    def __str__(self):
        return f"{self.user} · {self.plan.code} · {self.status}"

    def approve(self, reviewer=None):
        """Approve the slip and extend the user's subscription atomically."""
        now = timezone.now()
        user = self.user
        base = user.subscription_until if (user.subscription_until and user.subscription_until > now) else now
        user.subscription_until = base + timezone.timedelta(days=self.plan.duration_days)
        user.tier = self.plan.tier
        user.save(update_fields=["tier", "subscription_until"])
        self.status = self.Status.APPROVED
        self.reviewed_at = now
        self.reviewed_by = reviewer
        self.save(update_fields=["status", "reviewed_at", "reviewed_by"])
