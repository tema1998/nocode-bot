from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from bot_service.main import app
from fastapi import HTTPException, status
from fastapi.testclient import TestClient


# Initialize a test client for the FastAPI application
client = TestClient(app)


# Fixture to mock the mailing service dependency
@pytest.fixture
def mock_mailing_service():
    with patch(
        "bot_service.services.mailing_service.MailingService"
    ) as mock_service:
        mock_instance = (
            AsyncMock()
        )  # Create an AsyncMock instance for async methods
        mock_service.return_value = mock_instance  # Set the return value of the patched service to the mock instance
        yield mock_instance  # Yield the mock instance for use in tests


@pytest.mark.asyncio
async def test_start_mailing_success(mock_mailing_service):
    """
    Test the successful start of a mailing operation.
    Mocks the `create_mailing` method to return a predefined response.
    Asserts the API returns the expected response and a 202 Accepted status.
    """
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
    """
    Test the scenario where the bot specified for mailing is not found.
    Mocks the `create_mailing` method to raise an HTTPException.
    Asserts the API returns a 404 Not Found status and the expected error message.
    """
    test_message = {"message": "Test message"}

    mock_mailing_service.create_mailing.side_effect = HTTPException(
        status_code=404, detail="Bot not found"
    )

    response = client.post("/api/v1/mailing/999/start/", json=test_message)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Bot not found"}


@pytest.mark.asyncio
async def test_start_mailing_internal_error(mock_mailing_service):
    """
    Test the scenario where an internal error occurs while starting the mailing.
    Mocks the `create_mailing` method to raise an HTTPException.
    Asserts the API returns a 500 Internal Server Error status and the expected error message.
    """
    test_message = {"message": "Test message"}

    mock_mailing_service.create_mailing.side_effect = HTTPException(
        status_code=500, detail="Internal server error"
    )

    response = client.post("/api/v1/mailing/1/start/", json=test_message)
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json() == {"detail": "Internal server error"}
