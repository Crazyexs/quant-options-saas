from django.contrib import admin
from django.utils import timezone

from .models import Payment, Plan


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "tier", "price_thb", "duration_days", "is_active")
    list_editable = ("price_thb", "duration_days", "is_active")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("user", "plan", "amount", "status", "created_at", "reviewed_by")
    list_filter = ("status", "plan")
    search_fields = ("user__email",)
    readonly_fields = ("created_at", "reviewed_at", "reviewed_by")
    actions = ("approve_payments", "reject_payments")

    @admin.action(description="Approve selected payments (unlock access)")
    def approve_payments(self, request, queryset):
        n = 0
        for payment in queryset.filter(status=Payment.Status.PENDING):
            payment.approve(reviewer=request.user)
            n += 1
        self.message_user(request, f"Approved {n} payment(s) and unlocked access.")

    @admin.action(description="Reject selected payments")
    def reject_payments(self, request, queryset):
        queryset.filter(status=Payment.Status.PENDING).update(
            status=Payment.Status.REJECTED, reviewed_at=timezone.now(),
            reviewed_by=request.user)
