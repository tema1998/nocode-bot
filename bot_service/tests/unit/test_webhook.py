import pytest
from bot_service.main import app
from fastapi import HTTPException, status
from fastapi.testclient import TestClient


app.user_middleware.clear()
app.middleware_stack = app.build_middleware_stack()

client = TestClient(app)

TEST_TOKEN = "test-secret"


@pytest.mark.asyncio
async def test_webhook_success(
    mock_webhook_service, mock_chain_handle_service
):
    """
    Test that a valid webhook request is handled successfully.
    Mocks the handle_webhook method to return a successful response,
    and asserts that the API returns a 200 OK status with the expected response.
    """
    bot_id = 1
    update_data = {
        "message": {
            "text": "/start",
            "from": {"id": 123, "username": "test_user"},
        }
    }

    mock_webhook_service.handle_webhook.return_value = {"status": "ok"}

    response = client.post(
        f"/api/v1/webhook/{bot_id}",
        headers={"X-Telegram-Bot-Api-Secret-Token": TEST_TOKEN},
        json=update_data,
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "ok"}
    mock_webhook_service.handle_webhook.assert_awaited_once_with(
        bot_id, update_data, "test-secret"
    )


@pytest.mark.asyncio
async def test_webhook_bot_not_found(
    mock_webhook_service, mock_chain_handle_service
):
    """
    Test handling a case where the bot ID is not found.
    Mocks the handle_webhook method to raise an HTTPException for a not found bot,
    and asserts that the API returns a 404 Not Found status with the corresponding message.
    """
    bot_id = 999
    update_data = {
        "message": {
            "text": "/start",
            "from": {"id": 123, "username": "test_user"},
        }
    }

    mock_webhook_service.handle_webhook.side_effect = HTTPException(
        status_code=404, detail="Bot not found"
    )

    response = client.post(
        f"/api/v1/webhook/{bot_id}",
        headers={"X-Telegram-Bot-Api-Secret-Token": TEST_TOKEN},
        json=update_data,
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Bot not found"}


@pytest.mark.asyncio
async def test_webhook_bot_deactivated(
    mock_webhook_service, mock_chain_handle_service
):
    """
    Test handling a case where the bot is deactivated.
    Mocks the handle_webhook method to raise an HTTPException for a deactivated bot,
    and asserts that the API returns a 403 Forbidden status with the corresponding message.
    """
    bot_id = 1
    update_data = {
        "message": {
            "text": "/start",
            "from": {"id": 123, "username": "test_user"},
        }
    }

    mock_webhook_service.handle_webhook.side_effect = HTTPException(
        status_code=403, detail="Bot is deactivated."
    )

    response = client.post(
        f"/api/v1/webhook/{bot_id}",
        headers={"X-Telegram-Bot-Api-Secret-Token": TEST_TOKEN},
        json=update_data,
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "Bot is deactivated."}


@pytest.mark.asyncio
async def test_webhook_invalid_update_data(
    mock_webhook_service, mock_chain_handle_service
):
    """
    Test handling a case with invalid update data.
    Mocks the handle_webhook method to raise an HTTPException for improperly formatted update data,
    and asserts that the API returns a 400 Bad Request status with the corresponding message.
    """
    bot_id = 1
    update_data = {}  # Invalid update data

    mock_webhook_service.handle_webhook.side_effect = HTTPException(
        status_code=400, detail="Failed to parse update data."
    )

    response = client.post(
        f"/api/v1/webhook/{bot_id}",
        headers={"X-Telegram-Bot-Api-Secret-Token": TEST_TOKEN},
        json=update_data,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Failed to parse update data."}


@pytest.mark.asyncio
async def test_webhook_unsupported_update_type(
    mock_webhook_service, mock_chain_handle_service
):
    """
    Test handling a case with an unsupported update type.
    Mocks the handle_webhook method to raise an HTTPException for unsupported update types,
    and asserts that the API returns a 400 Bad Request status with the corresponding message.
    """
    bot_id = 1
    update_data = {
        "callback_query": {
            "data": "some_data",
            "from": {"id": 123, "username": "test_user"},
        }
    }

    mock_webhook_service.handle_webhook.side_effect = HTTPException(
        status_code=400, detail="Unsupported update type."
    )

    response = client.post(
        f"/api/v1/webhook/{bot_id}",
        headers={"X-Telegram-Bot-Api-Secret-Token": TEST_TOKEN},
        json=update_data,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Unsupported update type."}
