import logging.config

from bot_management.settings.apps import *
from bot_management.settings.auth import *
from bot_management.settings.base import *
from bot_management.settings.database import *
from bot_management.settings.internationalization import *
from bot_management.settings.logging import *
from bot_management.settings.static import *
from bot_management.settings.urls import *


LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
}

logging.config.dictConfig(LOGGING)

for logger in logging.Logger.manager.loggerDict.values():
    if isinstance(logger, logging.Logger):
        logger.disabled = True

logging.getLogger().disabled = True

DATABASES["default"] = {  # type:ignore
    "ENGINE": "django.db.backends.sqlite3",
    "NAME": ":memory:",
}
