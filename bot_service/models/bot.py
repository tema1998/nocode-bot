from bot_service.models.mixin import TimeStampedMixin
from pydantic.v1 import ConfigDict
from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    ForeignKey,
    Index,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from .base import Base


class Bot(Base, TimeStampedMixin):
    """Model representing a chatbot."""

    __tablename__ = "bots"
    id = Column(Integer, primary_key=True, index=True)
    is_active = Column(Boolean, default=True)
    token = Column(String, unique=True)
    secret_token = Column(String)
    default_reply = Column(String(3000), nullable=True, default="")
    username = Column(String)

    main_menu = relationship(
        "MainMenu",
        back_populates="bot",
        cascade="all, delete-orphan",
        passive_deletes=True,
        uselist=False,
    )

    buttons = relationship(
        "Button",
        back_populates="bot",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    chains = relationship(
        "Chain",
        back_populates="bot",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    users = relationship(
        "BotUser",
        back_populates="bot",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    user_states = relationship(
        "UserState",
        backref="bot",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    __table_args__ = (
        Index("idx_bot_token", "token", unique=True),
        Index("idx_bot_username", "username"),
    )


class BotUser(Base, TimeStampedMixin):
    """Model representing a bot user."""

    __tablename__ = "bot_users"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)  # Telegram user_id
    bot_id = Column(
        Integer, ForeignKey("bots.id", ondelete="CASCADE"), nullable=False
    )
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)

    bot = relationship("Bot", back_populates="users")

    model_config = ConfigDict(from_attributes=True)  # type: ignore

    __table_args__ = (
        Index("idx_bot_user_unique", "bot_id", "user_id", unique=True),
        Index("idx_botuser_created_at", "created_at"),
    )
