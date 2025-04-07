from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
)
from sqlalchemy.inspection import inspect


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
