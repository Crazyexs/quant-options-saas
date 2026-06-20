"""
allauth social adapter. LINE does not always return an email (the email scope
needs special approval), so we synthesize a stable placeholder from the provider
uid to satisfy our email-unique User model. Google returns a real email.
"""
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class SocialAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        if not getattr(user, "email", None):
            acc = sociallogin.account
            user.email = f"{acc.provider}_{acc.uid}@users.noreply.local"
        return user
