import datetime

import pytest
from bot_service.main import app
from bot_service.schemas.bot import BotUserSchema
from fastapi import HTTPException, status
from fastapi.testclient import TestClient


client = TestClient(app)


@pytest.mark.asyncio
async def test_get_bot_success(mock_telegram_bot_service):
    mock_telegram_bot_service.get_bot_details.return_value = {
        "is_active": True,
        "token": "test_token",
        "username": "test_bot",
        "name": "Test Bot",
        "default_reply": "Hello!",
    }

    response = client.get("/api/v1/bot/1")
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
    mock_telegram_bot_service.get_bot_details.side_effect = HTTPException(
        status_code=404, detail="Bot not found"
    )

    response = client.get("/api/v1/bot/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Bot not found"}


@pytest.mark.asyncio
async def test_delete_bot_success(mock_telegram_bot_service):
    response = client.delete("/api/v1/bot/1")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    mock_telegram_bot_service.delete_bot.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_delete_bot_not_found(mock_telegram_bot_service):
    mock_telegram_bot_service.delete_bot.side_effect = HTTPException(
        status_code=404, detail="Bot not found"
    )

    response = client.delete("/api/v1/bot/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Bot not found"}


@pytest.mark.asyncio
async def test_update_bot_success(mock_telegram_bot_service):
    mock_telegram_bot_service.update_bot.return_value = {
        "is_active": False,
        "token": "new_token",
        "username": "updated_bot",
        "default_reply": "Updated reply",
    }

    response = client.patch(
        "/api/v1/bot/1",
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
    mock_telegram_bot_service.update_bot.return_value = {
        "is_active": False,
        "token": "original_token",
        "username": "original_bot",
        "default_reply": "Original reply",
    }

    response = client.patch("/api/v1/bot/1", json={"is_active": False})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "is_active": False,
        "token": "original_token",
        "username": "original_bot",
        "default_reply": "Original reply",
    }


@pytest.mark.asyncio
async def test_create_bot_success(mock_telegram_bot_service):
    mock_telegram_bot_service.create_bot.return_value = {
        "id": 1,
        "username": "new_bot",
    }

    response = client.post("/api/v1/bot/", json={"token": "valid_token"})
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {"id": 1, "username": "new_bot"}


@pytest.mark.asyncio
async def test_create_bot_invalid_token(mock_telegram_bot_service):
    mock_telegram_bot_service.create_bot.side_effect = HTTPException(
        status_code=400, detail="Bot token is not valid."
    )

    response = client.post("/api/v1/bot/", json={"token": "invalid_token"})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Bot token is not valid."}


@pytest.mark.asyncio
async def test_get_bot_users_success(mock_bot_service):
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

    response = client.get("/api/v1/bot/1/list/?offset=0&limit=3")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["total_count"] == 150
    assert len(data["users"]) == 3
    assert data["users"][0]["username"] == "user1"


@pytest.mark.asyncio
async def test_get_bot_users_default_pagination(mock_bot_service):
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

    response = client.get("/api/v1/bot/1/list/")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["total_count"] == 100
    assert len(data["users"]) == 100


@pytest.mark.asyncio
async def test_get_bot_users_empty(mock_bot_service):
    mock_bot_service.get_bot_users_count.return_value = 0
    mock_bot_service.get_bot_users_chunk.return_value = []

    response = client.get("/api/v1/bot/1/list/")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["total_count"] == 0
    assert data["users"] == []
