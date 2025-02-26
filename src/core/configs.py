import logging

from pydantic_settings import BaseSettings, SettingsConfigDict


# Настройка логирования
logging.basicConfig(
    level=logging.INFO,  # Уровень логирования
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # Формат логов
)

logger = logging.getLogger(__name__)  # Получаем объект логгера


class Config(BaseSettings):
    app_name: str = "API"

    bot_service_db_host: str = "127.0.0.1"
    bot_service_db_port: int = 5432
    bot_service_db_name: str = "db_name"
    bot_service_db_user: str = "db_user"
    bot_service_db_password: str = "qwerty"

    sqlalchemy_echo: bool = True

    broker_user: str = "user"
    broker_pass: str = "pass"
    broker_protocol: str = "amqp"
    broker_host: str = "127.0.0.1"
    broker_port: str = "5672"

    redis_pass: str = "redis_pass"
    redis_host: str = "127.0.0.1"
    redis_port: str = "6379"

    bot_token: str = "7213712931:31uTX763YDG36DBU"
    webhook_url: str = "url"
    secret_token: str = "token"

    @property
    def broker_url(self) -> str:
        return f"{self.broker_protocol}://{self.broker_user}:{self.broker_pass}@{self.broker_host}:{self.broker_port}//"

    @property
    def backend_url(self) -> str:
        return (
            f"redis://:{self.redis_pass}@{self.redis_host}:{self.redis_port}/0"
        )

    @property
    def dsn(self) -> str:
        return f"postgresql+asyncpg://{self.bot_service_db_user}:{self.bot_service_db_password}@{self.bot_service_db_host}:{self.bot_service_db_port}/{self.bot_service_db_name}"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


config = Config()
