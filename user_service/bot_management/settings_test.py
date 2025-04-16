from bot_management.settings.apps import *
from bot_management.settings.auth import *
from bot_management.settings.base import *
from bot_management.settings.database import *
from bot_management.settings.internationalization import *
from bot_management.settings.logging import *
from bot_management.settings.static import *
from bot_management.settings.urls import *


DATABASES["default"] = {  # type:ignore
    "ENGINE": "django.db.backends.sqlite3",
    "NAME": ":memory:",
}
