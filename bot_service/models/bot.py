from bot_service.db.db_utils import Base
from bot_service.models.mixin import TimeStampedMixin
from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String,
)
from sqlalchemy.orm import relationship


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
