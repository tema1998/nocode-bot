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
def mock_main_menu_service(mock_mailing_service):
    with patch(
        "bot_service.services.main_menu_service.MainMenuService"
    ) as mock_service, patch(
        "bot_service.services.main_menu_service.PostgresAsyncRepository"
    ) as mock_db_repo, patch(
        "bot_service.services.main_menu_service.TelegramApiRepository"
    ) as mock_tg_repo:
        mock_instance = AsyncMock()
        mock_service.return_value = mock_instance

        mock_db_repo.return_value = AsyncMock()
        mock_tg_repo.return_value = AsyncMock()

        mock_instance.mailing_service = mock_mailing_service

        yield mock_instance


@pytest.fixture
def mock_webhook_service():
    with patch(
        "bot_service.services.webhook_service.WebhookService"
    ) as mock_service:
        mock_instance = AsyncMock()
        mock_service.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_chain_handle_service():
    with patch(
        "bot_service.services.chain_handler_service.ChainHandlerService"
    ) as mock_service:
        mock_instance = AsyncMock()
        mock_service.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_mailing_service():
    with patch(
        "bot_service.services.mailing_service.MailingService"
    ) as mock_service, patch(
        "bot_service.services.mailing_service.RabbitMQRepository"
    ) as mock_broker_repo:
        mock_instance = AsyncMock()
        mock_service.return_value = mock_instance

        mock_broker_instance = AsyncMock()
        mock_broker_repo.return_value = mock_broker_instance

        mock_broker_instance.publish = AsyncMock()
        mock_broker_instance.connect = AsyncMock()
        mock_broker_instance.close = AsyncMock()

        yield mock_instance
