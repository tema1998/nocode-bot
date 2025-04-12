from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from bot_service.main import app
from fastapi import HTTPException, status
from fastapi.testclient import TestClient


client = TestClient(app)


@pytest.mark.asyncio
async def test_create_chain_step_success(mock_chain_step_service):
    test_step_data = {
        "chain_id": 1,
        "name": "Test Step",
        "message": "Test message",
        "text_input": False,
    }

    # Create a MagicMock that will return proper attribute values
    mock_step = MagicMock()
    mock_step.id = 1
    mock_step.chain_id = 1
    mock_step.name = "Test Step"
    mock_step.message = "Test message"
    mock_step.next_step_id = None
    mock_step.text_input = False

    mock_chain_step_service.create_chain_step.return_value = mock_step

    response = client.post("/api/v1/chain-step/", json=test_step_data)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        "id": 1,
        "chain_id": 1,
        "name": "Test Step",
        "message": "Test message",
        "next_step_id": None,
        "text_input": False,
    }


@pytest.mark.asyncio
async def test_create_chain_step_with_button_link(mock_chain_step_service):
    test_step_data = {
        "chain_id": 1,
        "name": "Test Step",
        "message": "Test message",
        "set_as_next_step_for_button_id": 1,
        "text_input": False,
    }

    # Create a MagicMock that will return proper attribute values
    mock_step = MagicMock()
    mock_step.id = 1
    mock_step.chain_id = 1
    mock_step.name = "Test Step"
    mock_step.message = "Test message"
    mock_step.next_step_id = None
    mock_step.text_input = False

    mock_chain_step_service.create_chain_step.return_value = mock_step

    response = client.post("/api/v1/chain-step/", json=test_step_data)
    assert response.status_code == status.HTTP_201_CREATED
    mock_chain_step_service.create_chain_step.assert_called_once()


@pytest.mark.asyncio
async def test_create_chain_step_failure(mock_chain_step_service):
    test_step_data = {
        "chain_id": 1,
        "name": "Test Step",
        "message": "Test message",
        "text_input": False,
    }

    mock_chain_step_service.create_chain_step.side_effect = HTTPException(
        status_code=500, detail="Failed to create chain step"
    )

    response = client.post("/api/v1/chain-step/", json=test_step_data)
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json() == {"detail": "Failed to create chain step"}


@pytest.mark.asyncio
async def test_get_chain_step_success(mock_chain_step_service):
    # Create a MagicMock that will return proper attribute values
    mock_step = MagicMock()
    mock_step.id = 1
    mock_step.chain_id = 1
    mock_step.name = "Test Step"
    mock_step.message = "Test message"
    mock_step.next_step_id = 2
    mock_step.text_input = True

    mock_chain_step_service.get_chain_step.return_value = mock_step

    response = client.get("/api/v1/chain-step/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": 1,
        "chain_id": 1,
        "name": "Test Step",
        "message": "Test message",
        "next_step_id": 2,
        "text_input": True,
    }


@pytest.mark.asyncio
async def test_get_chain_step_not_found(mock_chain_step_service):
    mock_chain_step_service.get_chain_step.side_effect = HTTPException(
        status_code=404, detail="Chain step with ID 999 not found"
    )

    response = client.get("/api/v1/chain-step/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Chain step with ID 999 not found"}


@pytest.mark.asyncio
async def test_update_chain_step_success(mock_chain_step_service):
    test_update_data = {
        "name": "Updated Step",
        "message": "Updated message",
        "next_step_id": 3,
        "text_input": False,
    }

    # Create a MagicMock that will return proper attribute values
    mock_step = MagicMock()
    mock_step.id = 1
    mock_step.chain_id = 1
    mock_step.name = "Updated Step"
    mock_step.message = "Updated message"
    mock_step.next_step_id = 3
    mock_step.text_input = False

    mock_chain_step_service.update_chain_step.return_value = mock_step

    response = client.patch("/api/v1/chain-step/1", json=test_update_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": 1,
        "chain_id": 1,
        "name": "Updated Step",
        "message": "Updated message",
        "next_step_id": 3,
        "text_input": False,
    }


@pytest.mark.asyncio
async def test_update_chain_step_partial(mock_chain_step_service):
    test_update_data = {"message": "Updated message"}

    # Create a MagicMock that will return proper attribute values
    mock_step = MagicMock()
    mock_step.id = 1
    mock_step.chain_id = 1
    mock_step.name = "Original Step"  # Keeps original value
    mock_step.message = "Updated message"
    mock_step.next_step_id = 2  # Keeps original value
    mock_step.text_input = True  # Keeps original value

    mock_chain_step_service.update_chain_step.return_value = mock_step

    response = client.patch("/api/v1/chain-step/1", json=test_update_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Updated message"


@pytest.mark.asyncio
async def test_update_chain_step_not_found(mock_chain_step_service):
    test_update_data = {"message": "Updated message"}

    mock_chain_step_service.update_chain_step.side_effect = HTTPException(
        status_code=404, detail="Chain step with ID 999 not found"
    )

    response = client.patch("/api/v1/chain-step/999", json=test_update_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Chain step with ID 999 not found"}


@pytest.mark.asyncio
async def test_delete_chain_step_success(mock_chain_step_service):
    response = client.delete("/api/v1/chain-step/1")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    mock_chain_step_service.delete_chain_step.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_delete_chain_step_not_found(mock_chain_step_service):
    mock_chain_step_service.delete_chain_step.side_effect = HTTPException(
        status_code=404, detail="Chain step with ID 999 not found"
    )

    response = client.delete("/api/v1/chain-step/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Chain step with ID 999 not found"}
