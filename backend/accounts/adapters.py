"""
allauth social adapter. Discord returns an email when the user granted the email
scope and has a verified email; if it's missing we synthesize a stable placeholder
from the provider uid to satisfy our email-unique User model.
"""
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class SocialAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        if not getattr(user, "email", None):
            acc = sociallogin.account
            user.email = f"{acc.provider}_{acc.uid}@users.noreply.local"
        return user
