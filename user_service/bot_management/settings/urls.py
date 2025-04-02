import os


LOGIN_URL = "/auth/login/"

BOT_SERVICE_API_URL = os.getenv(
    "BOT_SERVICE_API_URL", "http://127.0.0.1:8080/api/v1/"
)
