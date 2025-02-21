import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.inspection import inspect
from src.db.db_utils import Base


class TimeStampedMixin:
    created_at = Column(DateTime, default=datetime.now(), nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.now(),
        onupdate=datetime.now(),
        nullable=False,
    )


class UUIDMixin:
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )

    def to_dict(self) -> dict:
        """Convert the instance to a dictionary."""
        return {
            c.key: getattr(self, c.key)
            for c in inspect(self).mapper.column_attrs  # type: ignore
        }


class Command(Base):
    __tablename__ = "commands"
    id = Column(Integer, primary_key=True)
    command = Column(String, nullable=False, unique=True)
    response = Column(String, nullable=False)


class Button(Base):
    __tablename__ = "buttons"
    id = Column(Integer, primary_key=True)
    command_id = Column(Integer, ForeignKey("commands.id"))
    text = Column(String, nullable=False)
    callback_data = Column(String, nullable=False)
