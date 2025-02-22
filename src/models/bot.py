from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import relationship
from src.db.db_utils import Base


class TimeStampedMixin:
    created_at = Column(DateTime, default=datetime.now(), nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.now(),
        onupdate=datetime.now(),
        nullable=False,
    )

    def to_dict(self) -> dict:
        """Convert the instance to a dictionary."""
        return {
            c.key: getattr(self, c.key)
            for c in inspect(self).mapper.column_attrs  # type: ignore
        }


class Bot(Base):
    __tablename__ = "bots"
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True)
    secret_token = Column(String)
    name = Column(String)
    commands = relationship("Command", back_populates="bot")


class Command(Base):
    __tablename__ = "commands"
    id = Column(Integer, primary_key=True, index=True)
    command = Column(String)
    response = Column(String)
    bot_id = Column(Integer, ForeignKey("bots.id"))
    bot = relationship("Bot", back_populates="commands")


# class Button(Base):
#     __tablename__ = "buttons"
#     id = Column(Integer, primary_key=True)
#     command_id = Column(Integer, ForeignKey("commands.id"))
#     text = Column(String, nullable=False)
#     callback_data = Column(String, nullable=False)
