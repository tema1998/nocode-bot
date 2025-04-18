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


# Initialize a test client for the FastAPI application
client = TestClient(app)


@pytest.fixture
def mock_mailing_service():
    """
    Fixture to mock the Mailing Service.
    Provides an AsyncMock instance for use across test cases.
    """
    with patch(
        "bot_service.services.mailing_service.MailingService"
    ) as mock_service:
        mock_instance = (
            AsyncMock()
        )  # Create an AsyncMock instance for async methods
        mock_service.return_value = (
            mock_instance  # Set the return value for the service
        )
        yield mock_instance  # Yield the mock instance for use in tests


# Test getting the main menu successfully
@pytest.mark.asyncio
async def test_get_main_menu_success(mock_main_menu_service):
    """
    Test getting the main menu with a welcome message.
    Mocks the main menu service to return a predefined response and
    asserts that the API returns 200 OK with the expected menu structure.
    """
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


# Test scenario where the main menu is not found
@pytest.mark.asyncio
async def test_get_main_menu_not_found(mock_main_menu_service):
    """
    Test getting the main menu when it does not exist.
    Mocks the service to raise an HTTPException and asserts that the API
    responds with a 404 Not Found status and appropriate error message.
    """
    mock_main_menu_service.main_menu_with_welcome_message.side_effect = (
        HTTPException(status_code=404, detail="Bot's main menu not found")
    )

    response = client.get("/api/v1/main-menu/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Bot's main menu not found"}


# Test updating the welcome message successfully
@pytest.mark.asyncio
async def test_update_welcome_message_success(mock_main_menu_service):
    """
    Test updating the welcome message of the main menu.
    Mocks the service method to return the updated message and asserts that
    the API responds with a 200 OK status and the expected response.
    """
    test_data = {"welcome_message": "New welcome message"}
    expected_response = {"bot_id": 1, "welcome_message": "New welcome message"}
    mock_main_menu_service.update_welcome_message.return_value = (
        PatchWelcomeMessageResponse(**expected_response)
    )

    response = client.patch("/api/v1/main-menu/1", json=test_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected_response


# Test updating the welcome message when the main menu is not found
@pytest.mark.asyncio
async def test_update_welcome_message_not_found(mock_main_menu_service):
    """
    Test updating the welcome message when the main menu does not exist.
    Mocks the service method to raise an HTTPException and asserts that the API
    responds with a 404 Not Found status and the appropriate error message.
    """
    test_data = {"welcome_message": "New welcome message"}
    mock_main_menu_service.update_welcome_message.side_effect = HTTPException(
        status_code=404, detail="Bot's main menu not found"
    )

    response = client.patch("/api/v1/main-menu/999", json=test_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Bot's main menu not found"}


# Test getting a specific button successfully
@pytest.mark.asyncio
async def test_get_button_success(mock_main_menu_service):
    """
    Test retrieving a specific button from the main menu.
    Mocks the service method to return button details and asserts that
    the API returns a 200 OK status with the expected button information.
    """
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


# Test scenario where the requested button is not found
@pytest.mark.asyncio
async def test_get_button_not_found(mock_main_menu_service):
    """
    Test retrieving a button that does not exist.
    Mocks the service method to raise an HTTPException and asserts that
    the API responds with a 404 Not Found status and the appropriate error message.
    """
    mock_main_menu_service.get_main_menu_button.side_effect = HTTPException(
        status_code=404, detail="Button not found"
    )

    response = client.get("/api/v1/main-menu/button/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Button not found"}


# Test creating a new button successfully
@pytest.mark.asyncio
async def test_create_button_success(
    mock_main_menu_service, mock_mailing_service
):
    """
    Test creating a new button in the main menu.
    Mocks the service method to return the created button details and asserts
    that the API responds with a 201 Created status and the expected response.
    """
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


# Test creating a button that has duplicate text
@pytest.mark.asyncio
async def test_create_button_duplicate_text(mock_main_menu_service):
    """
    Test creating a button with a text that already exists.
    Mocks the service method to raise an HTTPException for duplicate text and
    asserts that the API responds with a 400 Bad Request status and the appropriate error message.
    """
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


# Test updating a button successfully
@pytest.mark.asyncio
async def test_update_button_success(
    mock_main_menu_service, mock_mailing_service
):
    """
    Test updating an existing button in the main menu.
    Mocks the service method to return the updated button details and asserts
    that the API responds with a 200 OK status and the expected response.
    """
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


# Test updating a button that is not found
@pytest.mark.asyncio
async def test_update_button_not_found(mock_main_menu_service):
    """
    Test updating a button that does not exist.
    Mocks the service method to raise an HTTPException and asserts that
    the API responds with a 404 Not Found status and the appropriate error message.
    """
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


# Test deleting a button successfully
@pytest.mark.asyncio
async def test_delete_button_success(
    mock_main_menu_service, mock_mailing_service
):
    """
    Test successfully deleting a button from the main menu.
    Asserts that the API responds with a 204 No Content status after deletion.
    """
    response = client.delete("/api/v1/main-menu/button/1")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    mock_main_menu_service.delete_main_menu_button.assert_awaited_once_with(1)


# Test deleting a button that is not found
@pytest.mark.asyncio
async def test_delete_button_not_found(mock_main_menu_service):
    """
    Test attempting to delete a button that does not exist.
    Mocks the service method to raise an HTTPException and asserts that
    the API responds with a 404 Not Found status and the appropriate error message.
    """
    mock_main_menu_service.delete_main_menu_button.side_effect = HTTPException(
        status_code=404, detail="Button not found"
    )

    response = client.delete("/api/v1/main-menu/button/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Button not found"}


# Test button text validation against forbidden text
@pytest.mark.asyncio
async def test_button_text_validation(mock_main_menu_service):
    """
    Test validation of forbidden button text (e.g., "/start").
    Mocks the service method to raise an HTTPException and asserts that
    the API responds with a 400 Bad Request status and the appropriate error message.
    """
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
