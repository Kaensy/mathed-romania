"""
Development settings for MathEd Romania.
"""
from .base import *  # noqa: F401, F403

# =============================================================================
# Core
# =============================================================================
DEBUG = True


# =============================================================================
# Database - Local PostgreSQL via Docker
# =============================================================================
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME", default="mathed_romania"),
        "USER": config("DB_USER", default="mathed_user"),
        "PASSWORD": config("DB_PASSWORD", default="mathed_local_pass"),
        "HOST": config("DB_HOST", default="localhost"),
        "PORT": config("DB_PORT", default="5432"),
    }
}


# =============================================================================
# Cache - Local Redis via Docker
# =============================================================================
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": config("REDIS_URL", default="redis://localhost:6379/0"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}


# =============================================================================
# CORS - Allow frontend dev server
# =============================================================================
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Vite dev server
    "http://127.0.0.1:5173",
]
CORS_ALLOW_CREDENTIALS = True


# =============================================================================
# JWT Cookie - Relax security for local dev
# =============================================================================
SIMPLE_JWT = {
    **SIMPLE_JWT,  # noqa: F405
    "AUTH_COOKIE_SECURE": False,  # No HTTPS in local dev
}


# =============================================================================
# Debug Toolbar
# =============================================================================
INSTALLED_APPS += ["debug_toolbar", "django_extensions"]  # noqa: F405
MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")  # noqa: F405
INTERNAL_IPS = ["127.0.0.1"]


# =============================================================================
# Email - Console backend for dev
# =============================================================================
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
