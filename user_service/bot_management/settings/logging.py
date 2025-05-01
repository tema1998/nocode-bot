import logging.config
from pathlib import Path


LOG_DIR = (
    Path(__file__).resolve().parent.parent.parent / "logs" / "user-service"
)
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "json",
            "filename": str(LOG_DIR / "user_service.log"),
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
            "encoding": "utf-8",
        },
    },
    "loggers": {
        "": {  # корень логгера
            "handlers": ["console", "file"],
            "level": "DEBUG",
        },
    },
}

logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)
