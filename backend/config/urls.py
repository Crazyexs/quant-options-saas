from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def health(_request):
    return JsonResponse({"status": "ok", "service": "quant-options-api"})


urlpatterns = [
    path("", health),
    path("admin/", admin.site.urls),
    path("api/auth/", include("accounts.urls")),
    path("api/billing/", include("billing.urls")),
    path("api/", include("market.urls")),
]

if settings.SOCIAL_AUTH_ENABLED:
    # allauth handles the OAuth dance at /accounts/<provider>/login/ ; on success
    # it redirects to LOGIN_REDIRECT_URL (our social_complete -> JWT -> frontend).
    urlpatterns += [path("accounts/", include("allauth.urls"))]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
