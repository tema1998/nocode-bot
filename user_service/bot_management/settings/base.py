import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(BASE_DIR.parent / ".env")

SECRET_KEY = os.getenv(
    "USER_SERVICE_SECRET_KEY", "DSAmdU3H783hs8M9S30k9xSi9d3KD"
)
DEBUG = bool(int(os.getenv("USER_SERVICE_DEBUG", 1)))
ALLOWED_HOSTS = [os.getenv("USER_SERVICE_ALLOWED_HOST", "*")]

ROOT_URLCONF = "bot_management.urls"
WSGI_APPLICATION = "bot_management.wsgi.application"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
