from datetime import datetime

from bot_service.db.db_utils import Base
from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String
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
    token = Column(String, unique=True, index=True)
    secret_token = Column(String)
    name = Column(String)
    commands = relationship("Command", back_populates="bot")


class Command(Base):
    """Model representing a command associated with a chatbot."""

    __tablename__ = "commands"
    id = Column(Integer, primary_key=True, index=True)
    command = Column(String)
    response = Column(String)
    bot_id = Column(Integer, ForeignKey("bots.id"))
    bot = relationship("Bot", back_populates="commands")


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
    text = Column(String)
    buttons = relationship(
        "Button", back_populates="step", foreign_keys="Button.step_id"
    )
    funnel = relationship("Funnel", back_populates="steps")


class Button(Base):
    """Model representing a button that triggers actions in a funnel step."""

    __tablename__ = "buttons"
    id = Column(Integer, primary_key=True, index=True)
    step_id = Column(Integer, ForeignKey("funnel_steps.id"))
    text = Column(String)
    next_step_id = Column(Integer, ForeignKey("funnel_steps.id"))
    step = relationship(
        "FunnelStep", back_populates="buttons", foreign_keys=[step_id]
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
