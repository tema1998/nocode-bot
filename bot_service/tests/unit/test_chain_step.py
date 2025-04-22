from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from bot_service.main import app
from fastapi import HTTPException, status
from fastapi.testclient import TestClient


# Initialize a test client for the FastAPI application
client = TestClient(app)


@pytest.mark.asyncio
async def test_create_chain_step_success(mock_chain_step_service):
    """
    Test the successful creation of a chain step.
    Mocks the `create_chain_step` method to return a predefined step structure.
    Asserts that the API returns the expected step details and a 201 Created status.
    """
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

    response = client.post("/api/v1/steps/", json=test_step_data)
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
    """
    Test creating a chain step that links to a button.
    Mocks the `create_chain_step` method to verify the correct call with the additional
    'set_as_next_step_for_button_id' parameter.
    Asserts that the API returns a 201 Created status.
    """
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

    response = client.post("/api/v1/steps/", json=test_step_data)
    assert response.status_code == status.HTTP_201_CREATED
    mock_chain_step_service.create_chain_step.assert_called_once()


@pytest.mark.asyncio
async def test_create_chain_step_failure(mock_chain_step_service):
    """
    Test the failure scenario when creating a chain step.
    Mocks the `create_chain_step` method to raise an HTTPException indicating failure.
    Asserts the API returns a 500 Internal Server Error status and the expected error message.
    """
    test_step_data = {
        "chain_id": 1,
        "name": "Test Step",
        "message": "Test message",
        "text_input": False,
    }

    mock_chain_step_service.create_chain_step.side_effect = HTTPException(
        status_code=500, detail="Failed to create chain step"
    )

    response = client.post("/api/v1/steps/", json=test_step_data)
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json() == {"detail": "Failed to create chain step"}


@pytest.mark.asyncio
async def test_get_chain_step_success(mock_chain_step_service):
    """
    Test the successful retrieval of a chain step.
    Mocks the `get_chain_step` method to return a predefined step structure.
    Asserts that the API returns the expected step details and a 200 OK status.
    """
    # Create a MagicMock that will return proper attribute values
    mock_step = MagicMock()
    mock_step.id = 1
    mock_step.chain_id = 1
    mock_step.name = "Test Step"
    mock_step.message = "Test message"
    mock_step.next_step_id = 2
    mock_step.text_input = True

    mock_chain_step_service.get_chain_step.return_value = mock_step

    response = client.get("/api/v1/steps/1")
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
    """
    Test the scenario where a requested chain step is not found.
    Mocks the `get_chain_step` method to raise an HTTPException indicating the step was not found.
    Asserts that the API returns a 404 Not Found status and the expected error message.
    """
    mock_chain_step_service.get_chain_step.side_effect = HTTPException(
        status_code=404, detail="Chain step with ID 999 not found"
    )

    response = client.get("/api/v1/steps/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Chain step with ID 999 not found"}


@pytest.mark.asyncio
async def test_update_chain_step_success(mock_chain_step_service):
    """
    Test the successful update of a chain step.
    Mocks the `update_chain_step` method to return a predefined updated step structure.
    Asserts that the API returns the updated step's details and a 200 OK status.
    """
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

    response = client.patch("/api/v1/steps/1", json=test_update_data)
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
    """
    Test the partial update of a chain step.
    Mocks the `update_chain_step` method to return a step with the updated value for
    the message while keeping other fields unchanged.
    Asserts that the API returns the updated step's details and a 200 OK status.
    """
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

    response = client.patch("/api/v1/steps/1", json=test_update_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Updated message"


@pytest.mark.asyncio
async def test_update_chain_step_not_found(mock_chain_step_service):
    """
    Test the scenario where attempting to update a chain step that does not exist.
    Mocks the `update_chain_step` method to raise an HTTPException indicating the step was not found.
    Asserts the API returns a 404 Not Found status and the expected error message.
    """
    test_update_data = {"message": "Updated message"}

    mock_chain_step_service.update_chain_step.side_effect = HTTPException(
        status_code=404, detail="Chain step with ID 999 not found"
    )

    response = client.patch("/api/v1/steps/999", json=test_update_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Chain step with ID 999 not found"}


@pytest.mark.asyncio
async def test_delete_chain_step_success(mock_chain_step_service):
    """
    Test the successful deletion of a chain step.
    Asserts that the API returns a 204 No Content status after a successful delete operation.
    Also verifies that the delete method on the mock service was called with the correct ID.
    """
    response = client.delete("/api/v1/steps/1")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    mock_chain_step_service.delete_chain_step.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_delete_chain_step_not_found(mock_chain_step_service):
    """
    Test the scenario where attempting to delete a chain step that does not exist.
    Mocks the `delete_chain_step` method to raise an HTTPException indicating the step was not found.
    Asserts the API returns a 404 Not Found status and the expected error message.
    """
    mock_chain_step_service.delete_chain_step.side_effect = HTTPException(
        status_code=404, detail="Chain step with ID 999 not found"
    )

    response = client.delete("/api/v1/steps/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Chain step with ID 999 not found"}
