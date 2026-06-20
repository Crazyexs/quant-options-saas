from urllib.parse import urlencode

from django.conf import settings
from django.http import HttpResponseRedirect
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import RegisterSerializer, UserSerializer


class RegisterView(generics.CreateAPIView):
    """Email + password signup (MVP). Social login is wired via allauth."""
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


def social_complete(request):
    """
    allauth logs the user into a session after a successful LINE/Google OAuth and
    redirects here. We mint a JWT and bounce to the frontend callback with the
    tokens in the query string, then the SPA stores them. Plain Django view (uses
    the session user), not DRF.
    """
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return HttpResponseRedirect(f"{settings.FRONTEND_URL}/login?error=social")
    refresh = RefreshToken.for_user(user)
    qs = urlencode({"access": str(refresh.access_token), "refresh": str(refresh)})
    return HttpResponseRedirect(f"{settings.FRONTEND_URL}/auth/callback?{qs}")
