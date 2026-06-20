import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Plan",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True,
                                           serialize=False, verbose_name="ID")),
                ("code", models.CharField(max_length=32, unique=True)),
                ("name", models.CharField(max_length=80)),
                ("tier", models.CharField(
                    choices=[("free", "Free"), ("pro", "Pro"), ("elite", "Elite")],
                    default="pro", max_length=10)),
                ("price_thb", models.DecimalField(decimal_places=2, max_digits=10)),
                ("duration_days", models.PositiveIntegerField(default=30)),
                ("is_active", models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name="Payment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True,
                                           serialize=False, verbose_name="ID")),
                ("slip", models.ImageField(upload_to="slips/%Y/%m/")),
                ("amount", models.DecimalField(decimal_places=2, max_digits=10)),
                ("status", models.CharField(
                    choices=[("pending", "Pending"), ("approved", "Approved"),
                             ("rejected", "Rejected")],
                    default="pending", max_length=10)),
                ("note", models.CharField(blank=True, max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("reviewed_at", models.DateTimeField(blank=True, null=True)),
                ("plan", models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT, to="billing.plan")),
                ("reviewed_by", models.ForeignKey(
                    blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                    related_name="reviewed_payments", to=settings.AUTH_USER_MODEL)),
                ("user", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="payments", to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
