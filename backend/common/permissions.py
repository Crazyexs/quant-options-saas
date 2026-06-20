"""Tier-gating permission. Usage: permission_classes = [RequireTier("pro")]."""
from rest_framework.permissions import BasePermission


def RequireTier(min_tier: str):
    class _HasTier(BasePermission):
        message = f"This feature requires the '{min_tier}' plan or higher."

        def has_permission(self, request, view):
            user = getattr(request, "user", None)
            return bool(user and user.is_authenticated and user.has_tier(min_tier))

    return _HasTier
