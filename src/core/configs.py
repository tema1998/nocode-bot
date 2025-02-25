import logging

from pydantic_settings import BaseSettings, SettingsConfigDict


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


class Config(BaseSettings):
    app_name: str = "API"

    db_host: str = "127.0.0.1"
    db_port: int = 5432
    db_name: str = "db_name"
    db_user: str = "db_user"
    db_password: str = "qwerty"

    sqlalchemy_echo: bool = True

    broker_user: str = "user"
    broker_pass: str = "pass"
    broker_protocol: str = "amqp"
    broker_host: str = "127.0.0.1"
    broker_port: str = "5672"

    redis_pass: str = "redis_pass"
    redis_host: str = "127.0.0.1"
    redis_port: str = "6379"

    webhook_url: str = "url"

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
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


config = Config()
