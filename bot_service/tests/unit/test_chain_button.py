from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from bot_service.main import app
from fastapi import HTTPException, status
from fastapi.testclient import TestClient


client = TestClient(app)


@pytest.mark.asyncio
async def test_create_chain_button_success(mock_chain_button_service):
    test_button_data = {"step_id": 1, "text": "Test Button"}

    mock_button = MagicMock()
    mock_button.id = 1
    mock_button.step_id = 1
    mock_button.text = "Test Button"
    mock_button.next_step_id = None

    mock_chain_button_service.create_chain_button.return_value = mock_button

    response = client.post("/api/v1/chain-button/", json=test_button_data)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        "id": 1,
        "step_id": 1,
        "text": "Test Button",
        "next_step_id": None,
    }


@pytest.mark.asyncio
async def test_create_chain_button_failure(mock_chain_button_service):
    test_button_data = {"step_id": 1, "text": "Test Button"}

    mock_chain_button_service.create_chain_button.side_effect = HTTPException(
        status_code=500, detail="Failed to create chain button"
    )

    response = client.post("/api/v1/chain-button/", json=test_button_data)
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json() == {"detail": "Failed to create chain button"}


@pytest.mark.asyncio
async def test_get_chain_button_success(mock_chain_button_service):
    mock_button = MagicMock()
    mock_button.id = 1
    mock_button.step_id = 1
    mock_button.text = "Test Button"
    mock_button.next_step_id = 2

    mock_chain_button_service.get_chain_button.return_value = mock_button

    response = client.get("/api/v1/chain-button/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": 1,
        "step_id": 1,
        "text": "Test Button",
        "next_step_id": 2,
    }


@pytest.mark.asyncio
async def test_get_chain_button_not_found(mock_chain_button_service):
    mock_chain_button_service.get_chain_button.side_effect = HTTPException(
        status_code=404, detail="Chain button with ID 999 not found"
    )

    response = client.get("/api/v1/chain-button/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Chain button with ID 999 not found"}


@pytest.mark.asyncio
async def test_update_chain_button_success(mock_chain_button_service):
    test_update_data = {"text": "Updated Button", "next_step_id": 3}

    mock_button = MagicMock()
    mock_button.id = 1
    mock_button.step_id = 1
    mock_button.text = "Updated Button"
    mock_button.next_step_id = 3

    mock_chain_button_service.update_chain_button.return_value = mock_button

    response = client.patch("/api/v1/chain-button/1", json=test_update_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": 1,
        "step_id": 1,
        "text": "Updated Button",
        "next_step_id": 3,
    }


@pytest.mark.asyncio
async def test_update_chain_button_partial(mock_chain_button_service):
    test_update_data = {"text": "Updated Button"}

    mock_button = MagicMock()
    mock_button.id = 1
    mock_button.step_id = 1
    mock_button.text = "Updated Button"
    mock_button.next_step_id = 2

    mock_chain_button_service.update_chain_button.return_value = mock_button

    response = client.patch("/api/v1/chain-button/1", json=test_update_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": 1,
        "step_id": 1,
        "text": "Updated Button",
        "next_step_id": 2,
    }


@pytest.mark.asyncio
async def test_update_chain_button_not_found(mock_chain_button_service):
    test_update_data = {"text": "Updated Button"}

    mock_chain_button_service.update_chain_button.side_effect = HTTPException(
        status_code=404, detail="Chain button with ID 999 not found"
    )

    response = client.patch("/api/v1/chain-button/999", json=test_update_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Chain button with ID 999 not found"}


@pytest.mark.asyncio
async def test_delete_chain_button_success(mock_chain_button_service):
    response = client.delete("/api/v1/chain-button/1")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    mock_chain_button_service.delete_chain_button.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_delete_chain_button_not_found(mock_chain_button_service):
    mock_chain_button_service.delete_chain_button.side_effect = HTTPException(
        status_code=404, detail="Chain button with ID 999 not found"
    )

    response = client.delete("/api/v1/chain-button/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Chain button with ID 999 not found"}


@pytest.mark.asyncio
async def test_set_next_chain_step_success(mock_chain_button_service):
    test_data = {"next_chain_step_id": 2}

    mock_chain_button_service.set_next_chain_step_to_button.return_value = None

    response = client.post(
        "/api/v1/chain-button/set-next-step/1", json=test_data
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "message": "Next chain step for button updated successfully"
    }


@pytest.mark.asyncio
async def test_set_next_chain_step_button_not_found(mock_chain_button_service):
    test_data = {"next_chain_step_id": 2}

    mock_chain_button_service.set_next_chain_step_to_button.side_effect = (
        HTTPException(status_code=404, detail="Button with ID 999 not found.")
    )

    response = client.post(
        "/api/v1/chain-button/set-next-step/999", json=test_data
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Button with ID 999 not found."}


@pytest.mark.asyncio
async def test_set_next_chain_step_invalid(mock_chain_button_service):
    test_data = {"next_chain_step_id": 1}

    mock_chain_button_service.set_next_chain_step_to_button.side_effect = (
        HTTPException(
            status_code=400,
            detail="Cannot set the current step as the next step.",
        )
    )

    response = client.post(
        "/api/v1/chain-button/set-next-step/1", json=test_data
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "detail": "Cannot set the current step as the next step."
    }
