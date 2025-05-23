from sqlalchemy import (
    JSON,
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
from .mixin import TimeStampedMixin


class UserState(Base, TimeStampedMixin):
    __tablename__ = "user_state"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)
    bot_id = Column(
        Integer, ForeignKey("bots.id", ondelete="CASCADE"), nullable=False
    )
    chain_id = Column(
        Integer, ForeignKey("chains.id", ondelete="CASCADE"), nullable=True
    )
    step_id = Column(Integer, ForeignKey("chain_steps.id"), nullable=True)
    expects_text_input = Column(Boolean, default=False)
    result = Column(JSON, nullable=True)
    last_message_id = Column(Integer, nullable=True, default=None)

    chain = relationship("Chain", foreign_keys=[chain_id])
    step = relationship("ChainStep", foreign_keys=[step_id])

    __table_args__ = (
        Index("idx_userstate_user_expects", "user_id", "expects_text_input"),
        Index("idx_userstate_updated_at", "updated_at"),
        Index("idx_userstate_user_bot", "user_id", "bot_id"),
    )


class Chain(Base):
    __tablename__ = "chains"

    id = Column(Integer, primary_key=True, autoincrement=True)
    bot_id = Column(
        Integer, ForeignKey("bots.id", ondelete="CASCADE"), nullable=False
    )
    name = Column(String, nullable=False, unique=True)
    first_chain_step_id = Column(
        Integer,
        ForeignKey("chain_steps.id", ondelete="SET NULL"),
        nullable=True,
    )

    first_chain_step = relationship(
        "ChainStep", foreign_keys=[first_chain_step_id], post_update=True
    )
    buttons = relationship(
        "Button",
        back_populates="chain",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    steps = relationship(
        "ChainStep",
        back_populates="chain",
        cascade="all, delete-orphan",
        passive_deletes=True,
        foreign_keys="[ChainStep.chain_id]",
    )
    bot = relationship("Bot", back_populates="chains")

    __table_args__ = (
        Index("idx_chain_bot_id", "bot_id"),
        Index("idx_chain_first_step", "first_chain_step_id"),
        Index("idx_chain_name_bot_id", "name", "bot_id"),
    )


class ChainButton(Base):
    __tablename__ = "chain_buttons"

    id = Column(Integer, primary_key=True, autoincrement=True)
    step_id = Column(
        Integer,
        ForeignKey("chain_steps.id", ondelete="CASCADE"),
        nullable=False,
    )
    text = Column(String, nullable=False)
    next_step_id = Column(
        Integer,
        ForeignKey("chain_steps.id", ondelete="SET NULL"),
        nullable=True,
    )

    step = relationship(
        "ChainStep", back_populates="chain_buttons", foreign_keys=[step_id]
    )

    __table_args__ = (
        Index("idx_chainbutton_step_id", "step_id"),
        Index("idx_chainbutton_next_step_id", "next_step_id"),
        Index("idx_chainbutton_text_step_id", "text", "step_id"),
    )


class ChainStep(Base):
    __tablename__ = "chain_steps"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chain_id = Column(
        Integer, ForeignKey("chains.id", ondelete="CASCADE"), nullable=False
    )
    name = Column(String, nullable=False)
    message = Column(String, nullable=False)
    next_step_id = Column(
        Integer,
        ForeignKey("chain_steps.id", ondelete="SET NULL"),
        nullable=True,
    )
    text_input = Column(Boolean, default=False)

    chain_buttons = relationship(
        "ChainButton",
        back_populates="step",
        cascade="all, delete-orphan",
        passive_deletes=True,
        foreign_keys=[ChainButton.step_id],
        overlaps="buttons",
    )

    chain = relationship(
        "Chain", back_populates="steps", foreign_keys=[chain_id]
    )

    next_step = relationship(
        "ChainStep", foreign_keys=[next_step_id], remote_side=[id]
    )
    __table_args__ = (
        Index("idx_chainstep_chain_id", "chain_id"),
        Index("idx_chainstep_next_step_id", "next_step_id"),
        Index("idx_chainstep_name", "name"),
    )
