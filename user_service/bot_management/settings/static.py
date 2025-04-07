import os

from .base import BASE_DIR


STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")  # Куда собирать статику
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),  # Доп. директории со статикой
]

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
