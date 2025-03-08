from datetime import datetime

from bot_service.db.db_utils import Base
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import relationship


class TimeStampedMixin:
    """Mixin class that adds created_at and updated_at timestamp fields."""

    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        nullable=False,
    )

    def to_dict(self) -> dict:
        """Convert the instance to a dictionary.

        Returns:
            dict: A dictionary representation of the instance.
        """
        return {
            c.key: getattr(self, c.key)
            for c in inspect(self).mapper.column_attrs  # type: ignore
        }


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


class Button(Base, TimeStampedMixin):
    """Model representing a buttons associated with a chatbot."""

    __tablename__ = "buttons"
    id = Column(Integer, primary_key=True, index=True)
    button_text = Column(String(64), nullable=False)
    reply_text = Column(String(3000), nullable=True)
    funnel_id = Column(Integer, ForeignKey("funnels.id"))
    funnel = relationship("Funnel")
    main_menu_id = Column(Integer, ForeignKey("main_menu.id"), nullable=True)
    main_menu = relationship("MainMenu", back_populates="buttons")
    bot_id = Column(Integer, ForeignKey("bots.id"))
    bot = relationship("Bot", back_populates="buttons")


class MainMenu(Base):
    """Model representing the main menu of a chatbot."""

    __tablename__ = "main_menu"
    id = Column(Integer, primary_key=True, index=True)
    welcome_message = Column(String(3000), nullable=True)
    bot_id = Column(Integer, ForeignKey("bots.id"), nullable=False)
    bot = relationship("Bot", back_populates="main_menu")
    buttons = relationship("Button", back_populates="main_menu")


class Funnel(Base):
    """Model representing a funnel that groups steps for a chatbot."""

    __tablename__ = "funnels"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    bot_id = Column(Integer, ForeignKey("bots.id"))
    steps = relationship("FunnelStep", back_populates="funnel")


class FunnelStep(Base):
    """Model representing a step within a funnel."""

    __tablename__ = "funnel_steps"
    id = Column(Integer, primary_key=True, index=True)
    funnel_id = Column(Integer, ForeignKey("funnels.id"))
    text = Column(String(3000))
    funnel_buttons = relationship(
        "FunnelButton",
        back_populates="step",
        foreign_keys="FunnelButton.step_id",
    )
    funnel = relationship("Funnel", back_populates="steps")


class FunnelButton(Base):
    """Model representing a button that triggers actions in a funnel step."""

    __tablename__ = "funnel_buttons"
    id = Column(Integer, primary_key=True, index=True)
    step_id = Column(Integer, ForeignKey("funnel_steps.id"))
    text = Column(String)
    next_step_id = Column(Integer, ForeignKey("funnel_steps.id"))
    step = relationship(
        "FunnelStep", back_populates="funnel_buttons", foreign_keys=[step_id]
    )
    next_step = relationship("FunnelStep", foreign_keys=[next_step_id])


class UserState(Base):
    """Model representing the state of a user interacting with a chatbot."""

    __tablename__ = "user_states"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    bot_id = Column(Integer, ForeignKey("bots.id"))
    funnel_id = Column(Integer, ForeignKey("funnels.id"))
    current_step_id = Column(Integer, ForeignKey("funnel_steps.id"))
    data = Column(JSON)
