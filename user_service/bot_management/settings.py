import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent


load_dotenv(BASE_DIR.parent / ".env")

SECRET_KEY = os.getenv(
    "USER_SERVICE_SECRET_KEY", "DSAmdU3H783hs8M9S30k9xSi9d3KD"
)

DEBUG = bool(int(os.getenv("USER_SERVICE_DJANGO_DEBUG", 1)))
DEVELOPMENT = bool(int(os.getenv("USER_SERVICE_DJANGO_DEVELOPMENT", 1)))

ALLOWED_HOSTS = [
    os.getenv("USER_SERVICE_ALLOWED_HOST", "*"),
]

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "users",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "bot_management.urls"
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            TEMPLATE_DIR,
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "bot_management.wsgi.application"


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

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


STATIC_URL = "/static/"
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
MEDIA_URL = "/media/"

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")


# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
