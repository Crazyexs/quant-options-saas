"""
Django settings — env-driven. Local dev (no DATABASE_URL/REDIS_URL) falls back to
SQLite + local-memory cache so it runs with zero external services.
"""
import os
import sys
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# Make the copied quant modules (quant/gex_core.py, etc.) importable as top-level.
sys.path.insert(0, str(BASE_DIR / "quant"))


def _bool(name, default="false"):
    return os.getenv(name, default).lower() in ("1", "true", "yes", "on")


def _list(name, default=""):
    return [x.strip() for x in os.getenv(name, default).split(",") if x.strip()]


SECRET_KEY = os.getenv("SECRET_KEY", "dev-insecure-secret-change-me")
DEBUG = _bool("DEBUG", "true")
ALLOWED_HOSTS = _list("ALLOWED_HOSTS", "localhost,127.0.0.1")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    # third-party
    "rest_framework",
    "corsheaders",
    # local
    "accounts",
    "billing",
    "market",
]

# Social auth is optional for the MVP; enable by setting the provider keys.
SOCIAL_AUTH_ENABLED = bool(os.getenv("GOOGLE_CLIENT_ID") or os.getenv("LINE_CLIENT_ID"))
if SOCIAL_AUTH_ENABLED:
    INSTALLED_APPS += [
        "allauth", "allauth.account", "allauth.socialaccount",
        "allauth.socialaccount.providers.google",
        "allauth.socialaccount.providers.line",
    ]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
if SOCIAL_AUTH_ENABLED:
    MIDDLEWARE.append("allauth.account.middleware.AccountMiddleware")

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
SITE_ID = 1

TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [],
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
    ]},
}]

# Database: DATABASE_URL (Railway Postgres) else SQLite.
if os.getenv("DATABASE_URL"):
    DATABASES = {"default": dj_database_url.parse(os.environ["DATABASE_URL"], conn_max_age=600)}
else:
    DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}

# Cache: REDIS_URL (Railway Redis) else local memory.
if os.getenv("REDIS_URL"):
    CACHES = {"default": {"BACKEND": "django_redis.cache.RedisCache",
                          "LOCATION": os.environ["REDIS_URL"],
                          "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"}}}
else:
    CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

AUTH_USER_MODEL = "accounts.User"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.AllowAny",),
    "DEFAULT_THROTTLE_CLASSES": (
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ),
    "DEFAULT_THROTTLE_RATES": {"anon": "60/min", "user": "300/min"},
}

from datetime import timedelta  # noqa: E402
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=14),
}

CORS_ALLOWED_ORIGINS = _list("CORS_ALLOWED_ORIGINS", "http://localhost:3000")
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = _list("CSRF_TRUSTED_ORIGINS", "http://localhost:3000")

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Bangkok"
USE_I18N = True
USE_TZ = True

# Manual PromptPay config surfaced to the API.
PROMPTPAY_ID = os.getenv("PROMPTPAY_ID", "")
PROMPTPAY_NAME = os.getenv("PROMPTPAY_NAME", "")

# Shared market-data cache TTL (seconds) — matches CBOE ~delayed feed.
MARKET_CACHE_TTL = int(os.getenv("MARKET_CACHE_TTL", "90"))

# Frontend base URL — social login redirects back here with the JWT.
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# ── Social auth (LINE + Google via allauth) ───────────────────────────────────
if SOCIAL_AUTH_ENABLED:
    AUTHENTICATION_BACKENDS = [
        "django.contrib.auth.backends.ModelBackend",
        "allauth.account.auth_backends.AuthenticationBackend",
    ]
    # Headless: email-based, no username, no email verification step.
    ACCOUNT_USER_MODEL_USERNAME_FIELD = None
    ACCOUNT_USERNAME_REQUIRED = False
    ACCOUNT_EMAIL_REQUIRED = True
    ACCOUNT_AUTHENTICATION_METHOD = "email"
    ACCOUNT_EMAIL_VERIFICATION = "none"
    SOCIALACCOUNT_LOGIN_ON_GET = True          # /accounts/google/login/ redirects immediately
    SOCIALACCOUNT_ADAPTER = "accounts.adapters.SocialAdapter"
    # After allauth logs the user in, mint a JWT and bounce to the frontend.
    LOGIN_REDIRECT_URL = "/api/auth/social/complete/"
    SOCIALACCOUNT_PROVIDERS = {
        "google": {
            "APP": {"client_id": os.getenv("GOOGLE_CLIENT_ID", ""),
                    "secret": os.getenv("GOOGLE_CLIENT_SECRET", ""), "key": ""},
            "SCOPE": ["profile", "email"],
            "AUTH_PARAMS": {"access_type": "online"},
        },
        "line": {
            "APP": {"client_id": os.getenv("LINE_CLIENT_ID", ""),
                    "secret": os.getenv("LINE_CLIENT_SECRET", ""), "key": ""},
        },
    }

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
