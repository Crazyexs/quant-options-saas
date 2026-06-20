from rest_framework import serializers

from .models import Payment, Plan


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ("code", "name", "tier", "price_thb", "duration_days")


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ("id", "plan", "slip", "amount", "status", "created_at")
        read_only_fields = ("status", "created_at")
