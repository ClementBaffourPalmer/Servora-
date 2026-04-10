from .base import *  # noqa: F403

DEBUG = True

# Serve files from STATICFILES_DIRS (e.g. static/images/services/) without running collectstatic.
WHITENOISE_USE_FINDERS = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
    }
}

