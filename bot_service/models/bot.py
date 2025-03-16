from datetime import datetime

from bot_service.db.db_utils import Base
from sqlalchemy import (
    BigInteger,
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
    chains = relationship(
        "Chain", back_populates="bot", cascade="all, delete-orphan"
    )


class Button(Base, TimeStampedMixin):
    """Model representing a buttons associated with a chatbot."""

    __tablename__ = "buttons"
    id = Column(Integer, primary_key=True, index=True)
    button_text = Column(String(64), nullable=False)
    reply_text = Column(String(3000), nullable=True)
    main_menu_id = Column(Integer, ForeignKey("main_menu.id"), nullable=True)
    bot_id = Column(Integer, ForeignKey("bots.id"), index=True)
    chain_id = Column(Integer, ForeignKey("chains.id"), nullable=True)

    main_menu = relationship("MainMenu", back_populates="buttons")
    bot = relationship("Bot", back_populates="buttons")
    chain = relationship("Chain", back_populates="buttons")


class MainMenu(Base):
    """Model representing the main menu of a chatbot."""

    __tablename__ = "main_menu"
    id = Column(Integer, primary_key=True, index=True)
    welcome_message = Column(String(3000), nullable=True)
    bot_id = Column(Integer, ForeignKey("bots.id"), nullable=False)
    bot = relationship("Bot", back_populates="main_menu")
    buttons = relationship("Button", back_populates="main_menu")


class UserState(Base):
    __tablename__ = "user_state"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)  # ID пользователя в Telegram
    bot_id = Column(Integer, ForeignKey("bots.id"), nullable=False)  # ID бота
    chain_id = Column(
        Integer, ForeignKey("chains.id"), nullable=True
    )  # Текущая цепочка
    step_id = Column(
        Integer, ForeignKey("chain_steps.id"), nullable=True
    )  # Текущий шаг

    # Связь с цепочкой и шагом
    chain = relationship("Chain", foreign_keys=[chain_id])
    step = relationship("ChainStep", foreign_keys=[step_id])


class Chain(Base):
    __tablename__ = "chains"

    id = Column(Integer, primary_key=True, autoincrement=True)
    bot_id = Column(
        Integer, ForeignKey("bots.id"), nullable=False
    )  # Связь с ботом
    name = Column(String, nullable=False)  # Название цепочки
    start_message = Column(
        String, nullable=False
    )  # Начальное сообщение цепочки
    first_chain_step_id = Column(
        Integer, ForeignKey("chain_steps.id"), nullable=True
    )

    first_chain_step = relationship(
        "ChainStep", foreign_keys=[first_chain_step_id], post_update=True
    )
    buttons = relationship("Button", back_populates="chain")
    steps = relationship(
        "ChainStep",
        back_populates="chain",
        cascade="all, delete-orphan",
        foreign_keys="[ChainStep.chain_id]",
    )
    bot = relationship("Bot", back_populates="chains")


class ChainButton(Base):
    __tablename__ = "chain_buttons"

    id = Column(Integer, primary_key=True, autoincrement=True)
    step_id = Column(
        Integer, ForeignKey("chain_steps.id"), nullable=False
    )  # Связь с шагом
    text = Column(String, nullable=False)  # Текст кнопки
    callback = Column(String, nullable=True)  # Данные для callback

    # Keep the relationship to ChainStep, ensure foreign_keys are explicitly defined.
    step = relationship(
        "ChainStep", back_populates="chain_buttons", foreign_keys=[step_id]
    )

    # If using next_step, specify foreign key as well.
    next_step_id = Column(
        Integer, ForeignKey("chain_steps.id")
    )  # Ensure there is also a defined foreign key
    next_step = relationship("ChainStep", foreign_keys=[next_step_id])


class ChainStep(Base):
    __tablename__ = "chain_steps"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chain_id = Column(
        Integer, ForeignKey("chains.id"), nullable=False
    )  # Связь с цепочкой
    message = Column(String, nullable=False)  # Сообщение на этом шаге

    # Relationship to ChainButton
    chain_buttons = relationship(
        "ChainButton",
        back_populates="step",
        foreign_keys=[ChainButton.step_id],
    )

    # Specify foreign_keys argument explicitly to eliminate ambiguity
    buttons = relationship(
        "ChainButton",
        back_populates="step",
        cascade="all, delete-orphan",
        foreign_keys=[
            ChainButton.step_id
        ],  # Specify here which foreign key to use
    )

    chain = relationship(
        "Chain", back_populates="steps", foreign_keys=[chain_id]
    )
