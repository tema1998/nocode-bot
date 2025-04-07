import os

from .base import BASE_DIR


DATABASES = {
    "default": {
        "ENGINE": os.getenv(
            "USER_SERVICE_DB_ENGINE", "django.db.backends.sqlite3"
        ),
        "HOST": os.getenv("USER_SERVICE_DB_HOST"),
        "PORT": os.getenv("USER_SERVICE_DB_PORT"),
        "USER": os.getenv("USER_SERVICE_DB_USER"),
        "PASSWORD": os.getenv("USER_SERVICE_DB_PASSWORD"),
        "NAME": os.getenv("USER_SERVICE_DB_NAME", BASE_DIR / "db.sqlite3"),
    }
}
