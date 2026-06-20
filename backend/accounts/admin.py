from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ("email",)
    list_display = ("email", "tier", "subscription_until", "is_staff")
    list_filter = ("tier", "is_staff", "is_superuser")
    search_fields = ("email",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal", {"fields": ("first_name", "last_name")}),
        ("Access", {"fields": ("tier", "subscription_until")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser",
                                     "groups", "user_permissions")}),
    )
    add_fieldsets = ((None, {"classes": ("wide",),
                             "fields": ("email", "password1", "password2")}),)
