from unittest.mock import AsyncMock, patch

import pytest
from bot_service.main import app
from httpx import AsyncClient


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def mock_telegram_bot_service():
    with patch(
        "bot_service.services.telegram_bot_service.TelegramBotService"
    ) as mock_service:
        mock_instance = AsyncMock()
        mock_service.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_bot_service():
    with patch("bot_service.services.bot_service.BotService") as mock_service:
        mock_instance = AsyncMock()
        mock_service.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_chain_service():
    with patch(
        "bot_service.services.chain_service.ChainService"
    ) as mock_service:
        mock_instance = AsyncMock()
        mock_service.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_chain_button_service():
    with patch(
        "bot_service.services.chain_button_service.ChainButtonService"
    ) as mock_service:
        mock_instance = AsyncMock()
        mock_service.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_chain_step_service():
    with patch(
        "bot_service.services.chain_step_service.ChainStepService"
    ) as mock_service:
        mock_instance = AsyncMock()
        mock_service.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_mailing_service():
    with patch(
        "bot_service.services.mailing_service.MailingService"
    ) as mock_service:
        mock_instance = AsyncMock()
        mock_service.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_main_menu_service():
    with patch(
        "bot_service.services.main_menu_service.MainMenuService"
    ) as mock_service:
        mock_instance = AsyncMock()
        mock_service.return_value = mock_instance
        yield mock_instance
