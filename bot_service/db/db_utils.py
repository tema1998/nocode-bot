from typing import AsyncGenerator

from bot_service.core.configs import config
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker


Base = declarative_base()

# Create an asynchronous engine using the configuration DSN
engine = create_async_engine(
    config.dsn, echo=config.sqlalchemy_echo, future=True
)

# Create an asynchronous session factory
async_session_factory = sessionmaker(  # type: ignore
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


# Dependency to provide a session to FastAPI routes or other parts of the application
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session
