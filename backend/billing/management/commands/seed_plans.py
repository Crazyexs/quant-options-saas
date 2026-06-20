from django.core.management.base import BaseCommand

from accounts.models import Tier
from billing.models import Plan

PLANS = [
    ("pro_monthly",   "Pro (monthly)",   Tier.PRO,   590, 30),
    ("pro_yearly",    "Pro (yearly)",    Tier.PRO,   5900, 365),
    ("elite_monthly", "Elite (monthly)", Tier.ELITE, 1490, 30),
    ("elite_yearly",  "Elite (yearly)",  Tier.ELITE, 14900, 365),
]


class Command(BaseCommand):
    help = "Create / update the default subscription plans."

    def handle(self, *args, **opts):
        for code, name, tier, price, days in PLANS:
            obj, created = Plan.objects.update_or_create(
                code=code,
                defaults={"name": name, "tier": tier, "price_thb": price,
                          "duration_days": days, "is_active": True})
            self.stdout.write(("Created " if created else "Updated ") + obj.name)
        self.stdout.write(self.style.SUCCESS("Plans seeded."))
