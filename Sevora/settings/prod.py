from .base import *  # noqa: F403

DEBUG = False

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=False)  # type: ignore[name-defined] # noqa: F405

DATABASES = {
    "default": env.db(  # type: ignore[name-defined] # noqa: F405
        "DATABASE_URL",
        default="sqlite:///" + str(BASE_DIR / "db.sqlite3"),  # noqa: F405
    )
}

