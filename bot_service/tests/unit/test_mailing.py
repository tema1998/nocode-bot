from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from bot_service.main import app
from fastapi import HTTPException, status
from fastapi.testclient import TestClient


client = TestClient(app)


@pytest.fixture
def mock_bot_service():
    with patch("bot_service.services.bot_service.BotService") as mock_service:
        mock_instance = AsyncMock()
        mock_service.return_value = mock_instance
        yield mock_instance


@pytest.mark.asyncio
async def test_start_mailing_success(mock_mailing_service):
    test_message = {"message": "Test message"}
    expected_response = {
        "mailing_id": 123,
        "status": "started",
        "started_at": "2023-01-01T00:00:00",
        "bot_id": 1,
    }

    mock_mailing_service.create_mailing.return_value = expected_response

    response = client.post("/api/v1/mailing/1/start/", json=test_message)
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.json() == expected_response


@pytest.mark.asyncio
async def test_start_mailing_bot_not_found(mock_mailing_service):
    test_message = {"message": "Test message"}

    mock_mailing_service.create_mailing.side_effect = HTTPException(
        status_code=404, detail="Bot not found"
    )

    response = client.post("/api/v1/mailing/999/start/", json=test_message)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Bot not found"}


@pytest.mark.asyncio
async def test_start_mailing_internal_error(mock_mailing_service):
    test_message = {"message": "Test message"}

    mock_mailing_service.create_mailing.side_effect = HTTPException(
        status_code=500, detail="Internal server error"
    )

    response = client.post("/api/v1/mailing/1/start/", json=test_message)
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json() == {"detail": "Internal server error"}


@pytest.mark.asyncio
async def test_get_mailing_status_not_found(mock_mailing_service):
    mock_mailing_service.get_mailing_status.return_value = {
        "status": "not_found"
    }

    response = client.get("/api/v1/mailing/999/status/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "not_found"}


@pytest.mark.asyncio
async def test_get_mailing_status_in_progress(mock_mailing_service):
    mock_mailing_service.get_mailing_status.return_value = {
        "status": "in_progress"
    }

    response = client.get("/api/v1/mailing/123/status/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "in_progress"}


@pytest.mark.asyncio
async def test_get_mailing_status_completed(mock_mailing_service):
    completed_response = {
        "status": "completed",
        "result": {
            "total_users": 100,
            "success": 95,
            "failed": 5,
            "completed_at": "2023-01-01T00:01:00",
        },
    }
    mock_mailing_service.get_mailing_status.return_value = completed_response

    response = client.get("/api/v1/mailing/123/status/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == completed_response


@pytest.mark.asyncio
async def test_get_mailing_status_failed(mock_mailing_service):
    failed_response = {"status": "failed", "error": "Connection error"}
    mock_mailing_service.get_mailing_status.return_value = failed_response

    response = client.get("/api/v1/mailing/123/status/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == failed_response


@pytest.mark.asyncio
async def test_cancel_mailing_success(mock_mailing_service):
    mock_mailing_service.cancel_mailing.return_value = True

    response = client.post("/api/v1/mailing/123/cancel/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "cancelled"}


@pytest.mark.asyncio
async def test_cancel_mailing_not_cancelled(mock_mailing_service):
    mock_mailing_service.cancel_mailing.return_value = False

    response = client.post("/api/v1/mailing/123/cancel/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "not_cancelled"}
