import datetime

import pytest
from bot_service.main import app
from bot_service.schemas.bot import BotUserSchema
from fastapi import HTTPException, status
from fastapi.testclient import TestClient


client = TestClient(app)


@pytest.mark.asyncio
async def test_get_bot_success(mock_telegram_bot_service):
    """
    Test the successful retrieval of bot details.
    Mocks the `get_bot_details` method to return a predefined bot structure.
    Asserts that the API returns the expected bot details and a 200 OK status.
    """
    mock_telegram_bot_service.get_bot_details.return_value = {
        "is_active": True,
        "token": "test_token",
        "username": "test_bot",
        "name": "Test Bot",
        "default_reply": "Hello!",
    }

    response = client.get("/api/v1/bots/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "is_active": True,
        "token": "test_token",
        "username": "test_bot",
        "name": "Test Bot",
        "default_reply": "Hello!",
    }


@pytest.mark.asyncio
async def test_get_bot_not_found(mock_telegram_bot_service):
    """
    Test the scenario where a bot is not found.
    Mocks the `get_bot_details` method to raise an HTTPException indicating bot not found.
    Asserts that the API returns a 404 Not Found status and the expected error message.
    """
    mock_telegram_bot_service.get_bot_details.side_effect = HTTPException(
        status_code=404, detail="Bot not found"
    )

    response = client.get("/api/v1/bots/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Bot not found"}


@pytest.mark.asyncio
async def test_delete_bot_success(mock_telegram_bot_service):
    """
    Test the successful deletion of a bot.
    Asserts that the API returns a 204 No Content status after a successful delete operation.
    Also verifies that the delete method on the mock service was called with the correct ID.
    """
    response = client.delete("/api/v1/bots/1")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    mock_telegram_bot_service.delete_bot.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_delete_bot_not_found(mock_telegram_bot_service):
    """
    Test the scenario where a bot to be deleted is not found.
    Mocks the `delete_bot` method to raise an HTTPException indicating bot not found.
    Asserts that the API returns a 404 Not Found status and the expected error message.
    """
    mock_telegram_bot_service.delete_bot.side_effect = HTTPException(
        status_code=404, detail="Bot not found"
    )

    response = client.delete("/api/v1/bots/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Bot not found"}


@pytest.mark.asyncio
async def test_update_bot_success(mock_telegram_bot_service):
    """
    Test the successful update of a bot's details.
    Mocks the `update_bot` method to return a predefined updated bot structure.
    Asserts that the API returns the updated bot's details and a 200 OK status.
    """
    mock_telegram_bot_service.update_bot.return_value = {
        "is_active": False,
        "token": "new_token",
        "username": "updated_bot",
        "default_reply": "Updated reply",
    }

    response = client.patch(
        "/api/v1/bots/1",
        json={
            "is_active": False,
            "token": "new_token",
            "default_reply": "Updated reply",
        },
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "is_active": False,
        "token": "new_token",
        "username": "updated_bot",
        "default_reply": "Updated reply",
    }


@pytest.mark.asyncio
async def test_update_bot_partial_data(mock_telegram_bot_service):
    """
    Test the successful update of a bot's details with partial data.
    Mocks the `update_bot` method to simulate an update where only some fields are changed.
    Asserts that the returned bot structure reflects the update and returns a 200 OK status.
    """
    mock_telegram_bot_service.update_bot.return_value = {
        "is_active": False,
        "token": "original_token",
        "username": "original_bot",
        "default_reply": "Original reply",
    }

    response = client.patch("/api/v1/bots/1", json={"is_active": False})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "is_active": False,
        "token": "original_token",
        "username": "original_bot",
        "default_reply": "Original reply",
    }


@pytest.mark.asyncio
async def test_create_bot_success(mock_telegram_bot_service):
    """
    Test the successful creation of a new bot.
    Mocks the `create_bot` method to return a predefined bot ID and username.
    Asserts that the API returns the created bot's information and a 201 Created status.
    """
    mock_telegram_bot_service.create_bot.return_value = {
        "id": 1,
        "username": "new_bot",
    }

    response = client.post("/api/v1/bots/", json={"token": "valid_token"})
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {"id": 1, "username": "new_bot"}


@pytest.mark.asyncio
async def test_create_bot_invalid_token(mock_telegram_bot_service):
    """
    Test the scenario where invalid bot token is provided during creation.
    Mocks the `create_bot` method to raise an HTTPException indicating the token is invalid.
    Asserts that the API returns a 400 Bad Request status and the expected error message.
    """
    mock_telegram_bot_service.create_bot.side_effect = HTTPException(
        status_code=400, detail="Bot token is not valid."
    )

    response = client.post("/api/v1/bots/", json={"token": "invalid_token"})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Bot token is not valid."}


@pytest.mark.asyncio
async def test_get_bot_users_success(mock_bot_service):
    """
    Test the successful retrieval of bot users.
    Mocks the methods for counting and retrieving users for a bot.
    Asserts that the API returns the correct total count and user data in the response.
    """
    valid_user_data = {
        "id": 1,
        "user_id": 1,
        "bot_id": 1,
        "username": "user1",
        "first_name": "Test",
        "last_name": "User",
        "created_at": datetime.datetime.now().isoformat(),
        "updated_at": datetime.datetime.now().isoformat(),
    }

    mock_bot_service.get_bot_users_count.return_value = 150

    mock_bot_service.get_bot_users_chunk.return_value = [
        BotUserSchema(**valid_user_data),
        BotUserSchema(**{**valid_user_data, "id": 2, "username": "user2"}),
        BotUserSchema(**{**valid_user_data, "id": 3, "username": "user3"}),
    ]

    response = client.get("/api/v1/bots/1/users/?offset=0&limit=3")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["total_count"] == 150
    assert len(data["users"]) == 3
    assert data["users"][0]["username"] == "user1"


@pytest.mark.asyncio
async def test_get_bot_users_default_pagination(mock_bot_service):
    """
    Test the retrieval of bot users with default pagination.
    Mocks the methods for counting and retrieving users for a bot.
    Asserts that the API returns the correct total count and user data in the response.
    """
    valid_user_data = {
        "id": 1,
        "user_id": 1,
        "bot_id": 1,
        "username": "user1",
        "first_name": "Test",
        "last_name": "User",
        "created_at": datetime.datetime.now().isoformat(),
        "updated_at": datetime.datetime.now().isoformat(),
    }

    mock_bot_service.get_bot_users_count.return_value = 100
    mock_bot_service.get_bot_users_chunk.return_value = [
        BotUserSchema(**{**valid_user_data, "id": i, "username": f"user{i}"})
        for i in range(100)
    ]

    response = client.get("/api/v1/bots/1/users/")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["total_count"] == 100
    assert len(data["users"]) == 100


@pytest.mark.asyncio
async def test_get_bot_users_empty(mock_bot_service):
    """
    Test the scenario where there are no users associated with a bot.
    Mocks the methods for counting and retrieving users for a bot.
    Asserts that the API returns a total count of 0 and an empty user list in the response.
    """
    mock_bot_service.get_bot_users_count.return_value = 0
    mock_bot_service.get_bot_users_chunk.return_value = []

    response = client.get("/api/v1/bots/1/users/")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["total_count"] == 0
    assert data["users"] == []
