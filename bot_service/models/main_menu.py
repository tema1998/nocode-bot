from bot_service.models.mixin import TimeStampedMixin
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from .base import Base


class Button(Base, TimeStampedMixin):
    __tablename__ = "buttons"
    id = Column(Integer, primary_key=True, index=True)
    button_text = Column(String(64), nullable=False)
    reply_text = Column(String(3000), nullable=True)
    main_menu_id = Column(
        Integer, ForeignKey("main_menu.id", ondelete="CASCADE"), nullable=True
    )
    bot_id = Column(
        Integer, ForeignKey("bots.id", ondelete="CASCADE"), nullable=False
    )
    chain_id = Column(Integer, ForeignKey("chains.id"), nullable=True)

    main_menu = relationship("MainMenu", back_populates="buttons")
    bot = relationship("Bot", back_populates="buttons")
    chain = relationship("Chain", back_populates="buttons")


class MainMenu(Base):
    __tablename__ = "main_menu"
    id = Column(Integer, primary_key=True, index=True)
    welcome_message = Column(String(3000), nullable=True)
    bot_id = Column(
        Integer, ForeignKey("bots.id", ondelete="CASCADE"), nullable=False
    )
    bot = relationship("Bot", back_populates="main_menu")
    buttons = relationship(
        "Button",
        back_populates="main_menu",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
