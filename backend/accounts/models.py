from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone


class Tier(models.TextChoices):
    FREE = "free", "Free"
    PRO = "pro", "Pro"
    ELITE = "elite", "Elite"


TIER_RANK = {Tier.FREE: 0, Tier.PRO: 1, Tier.ELITE: 2}


class UserManager(BaseUserManager):
    """Email is the login identifier (no separate username)."""
    use_in_migrations = True

    def _create(self, email, password, **extra):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra):
        extra.setdefault("is_staff", False)
        extra.setdefault("is_superuser", False)
        return self._create(email, password, **extra)

    def create_superuser(self, email, password=None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        return self._create(email, password, **extra)


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    tier = models.CharField(max_length=10, choices=Tier.choices, default=Tier.FREE)
    # Paid access valid until this moment (None = free / never paid).
    subscription_until = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserManager()

    def __str__(self):
        return self.email

    @property
    def effective_tier(self) -> str:
        """Downgrade to free if the paid subscription has lapsed."""
        if self.tier != Tier.FREE:
            if self.subscription_until and self.subscription_until < timezone.now():
                return Tier.FREE
        return self.tier

    def has_tier(self, minimum: str) -> bool:
        return TIER_RANK.get(self.effective_tier, 0) >= TIER_RANK.get(minimum, 0)
