import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Create a superuser from DJANGO_SUPERUSER_EMAIL/PASSWORD if absent.

    Lets a free host (Render) provision the admin user at deploy time without an
    interactive shell. No-op if the env vars are missing or the user exists.
    """
    help = "Idempotently create a superuser from environment variables."

    def handle(self, *args, **opts):
        email = os.getenv("DJANGO_SUPERUSER_EMAIL")
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD")
        if not email or not password:
            self.stdout.write("DJANGO_SUPERUSER_EMAIL/PASSWORD not set; skipping.")
            return
        User = get_user_model()
        if User.objects.filter(email=email).exists():
            self.stdout.write(f"Superuser {email} already exists.")
            return
        User.objects.create_superuser(email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f"Created superuser {email}"))
