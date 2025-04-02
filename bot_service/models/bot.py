from bot_service.models.mixin import TimeStampedMixin
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
    token = Column(String, unique=True, index=True)
    secret_token = Column(String)
    default_reply = Column(String(3000), nullable=True, default="")
    username = Column(String)
    main_menu = relationship("MainMenu", back_populates="bot", uselist=False)
    buttons = relationship("Button", back_populates="bot")
    chains = relationship(
        "Chain", back_populates="bot", cascade="all, delete-orphan"
    )
    users = relationship(
        "BotUser", back_populates="bot", cascade="all, delete-orphan"
    )


class BotUser(Base, TimeStampedMixin):
    """Model representing a bot user."""

    __tablename__ = "bot_users"
    __table_args__ = (
        Index("idx_bot_user_unique", "bot_id", "id", unique=True),
        {"schema": "public"},
    )

    id = Column(
        BigInteger, primary_key=True
    )  # Telegram user_id как primary key
    bot_id = Column(
        Integer, ForeignKey("bots.id", ondelete="CASCADE"), nullable=False
    )
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)

    bot = relationship("Bot", back_populates="users")
