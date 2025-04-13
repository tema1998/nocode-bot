from unittest.mock import AsyncMock, patch

import pytest
from bot_service.main import app
from bot_service.schemas.main_menu import (
    ButtonResponse,
    ButtonUpdateResponse,
    PatchWelcomeMessageResponse,
)
from fastapi import HTTPException, status
from fastapi.testclient import TestClient


client = TestClient(app)


@pytest.fixture
def mock_mailing_service():
    with patch(
        "bot_service.services.mailing_service.MailingService"
    ) as mock_service:
        mock_instance = AsyncMock()
        mock_service.return_value = mock_instance
        yield mock_instance


@pytest.mark.asyncio
async def test_get_main_menu_success(mock_main_menu_service):
    mock_response = {
        "welcome_message": "Welcome!",
        "buttons": [
            {
                "id": 1,
                "bot_id": 1,
                "button_text": "Button 1",
                "reply_text": "Reply 1",
                "chain_id": 1,
                "chain": "chain_name",
            },
            {
                "id": 2,
                "bot_id": 1,
                "button_text": "Button 2",
                "reply_text": "Reply 2",
                "chain_id": 1,
                "chain": "chain_name",
            },
        ],
    }
    mock_main_menu_service.main_menu_with_welcome_message.return_value = (
        mock_response
    )

    response = client.get("/api/v1/main-menu/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == mock_response


@pytest.mark.asyncio
async def test_get_main_menu_not_found(mock_main_menu_service):
    mock_main_menu_service.main_menu_with_welcome_message.side_effect = (
        HTTPException(status_code=404, detail="Bot's main menu not found")
    )

    response = client.get("/api/v1/main-menu/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Bot's main menu not found"}


@pytest.mark.asyncio
async def test_update_welcome_message_success(mock_main_menu_service):
    test_data = {"welcome_message": "New welcome message"}
    expected_response = {"bot_id": 1, "welcome_message": "New welcome message"}
    mock_main_menu_service.update_welcome_message.return_value = (
        PatchWelcomeMessageResponse(**expected_response)
    )

    response = client.patch("/api/v1/main-menu/1", json=test_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected_response


@pytest.mark.asyncio
async def test_update_welcome_message_not_found(mock_main_menu_service):
    test_data = {"welcome_message": "New welcome message"}
    mock_main_menu_service.update_welcome_message.side_effect = HTTPException(
        status_code=404, detail="Bot's main menu not found"
    )

    response = client.patch("/api/v1/main-menu/999", json=test_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Bot's main menu not found"}


@pytest.mark.asyncio
async def test_get_button_success(mock_main_menu_service):
    mock_response = {
        "id": 1,
        "bot_id": 1,
        "button_text": "Button 1",
        "reply_text": "Reply 1",
        "chain_id": 1,
        "chain": "chain_name",
    }
    mock_main_menu_service.get_main_menu_button.return_value = ButtonResponse(
        **mock_response
    )

    response = client.get("/api/v1/main-menu/button/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == mock_response


@pytest.mark.asyncio
async def test_get_button_not_found(mock_main_menu_service):
    mock_main_menu_service.get_main_menu_button.side_effect = HTTPException(
        status_code=404, detail="Button not found"
    )

    response = client.get("/api/v1/main-menu/button/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Button not found"}


@pytest.mark.asyncio
async def test_create_button_success(
    mock_main_menu_service, mock_mailing_service
):
    test_data = {
        "bot_id": 1,
        "button_text": "New Button",
        "reply_text": "New Reply",
        "chain_id": 1,
    }
    mock_response = {
        "id": 3,
        "bot_id": 1,
        "button_text": "New Button",
        "reply_text": "New Reply",
        "chain_id": 1,
        "chain": "Chain",
    }
    mock_main_menu_service.create_main_menu_button.return_value = (
        ButtonResponse(**mock_response)
    )

    response = client.post("/api/v1/main-menu/button/", json=test_data)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == mock_response


@pytest.mark.asyncio
async def test_create_button_duplicate_text(mock_main_menu_service):
    test_data = {
        "bot_id": 1,
        "button_text": "Duplicate",
        "reply_text": "Reply",
        "chain_id": 1,
    }
    mock_main_menu_service.create_main_menu_button.side_effect = HTTPException(
        status_code=400, detail="A button with the same text already exists."
    )

    response = client.post("/api/v1/main-menu/button/", json=test_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "detail": "A button with the same text already exists."
    }


@pytest.mark.asyncio
async def test_update_button_success(
    mock_main_menu_service, mock_mailing_service
):
    test_data = {
        "button_text": "Updated Button",
        "reply_text": "Updated Reply",
    }
    mock_response = {
        "id": 1,
        "bot_id": 1,
        "button_text": "Updated Button",
        "reply_text": "Updated Reply",
        "chain_id": None,
        "chain": None,
    }
    mock_main_menu_service.update_main_menu_button.return_value = (
        ButtonUpdateResponse(**mock_response)
    )

    response = client.patch("/api/v1/main-menu/button/1", json=test_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == mock_response


@pytest.mark.asyncio
async def test_update_button_not_found(mock_main_menu_service):
    test_data = {
        "button_text": "Updated Button",
        "reply_text": "Updated Reply",
    }
    mock_main_menu_service.update_main_menu_button.side_effect = HTTPException(
        status_code=404, detail="Button not found"
    )

    response = client.patch("/api/v1/main-menu/button/999", json=test_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Button not found"}


@pytest.mark.asyncio
async def test_delete_button_success(
    mock_main_menu_service, mock_mailing_service
):
    response = client.delete("/api/v1/main-menu/button/1")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    mock_main_menu_service.delete_main_menu_button.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_delete_button_not_found(mock_main_menu_service):
    mock_main_menu_service.delete_main_menu_button.side_effect = HTTPException(
        status_code=404, detail="Button not found"
    )

    response = client.delete("/api/v1/main-menu/button/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Button not found"}


@pytest.mark.asyncio
async def test_button_text_validation(mock_main_menu_service):
    # Test forbidden button text "/start"
    test_data = {
        "bot_id": 1,
        "button_text": "/start",
        "reply_text": "Reply",
        "chain_id": 1,
    }
    mock_main_menu_service.create_main_menu_button.side_effect = HTTPException(
        status_code=400, detail="A button with this name is forbidden."
    )

    response = client.post("/api/v1/main-menu/button/", json=test_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "detail": "A button with this name is forbidden."
    }
