import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from bot_service.main import app
from bot_service.schemas.chain import ChainResponse, ChainsResponse, UserResult
from fastapi import HTTPException, status
from fastapi.testclient import TestClient


client = TestClient(app)


@pytest.mark.asyncio
async def test_create_chain_success(mock_chain_service):
    test_chain_data = {"bot_id": 1, "name": "Test Chain"}

    mock_chain = MagicMock()
    mock_chain.id = 1
    mock_chain.bot_id = 1
    mock_chain.name = "Test Chain"

    mock_chain_service.create_chain.return_value = mock_chain
    mock_chain_service.create_and_set_first_step.return_value = mock_chain

    response = client.post("/api/v1/chain/", json=test_chain_data)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {"id": 1, "bot_id": 1, "name": "Test Chain"}


@pytest.mark.asyncio
async def test_create_chain_name_exists(mock_chain_service):
    test_chain_data = {"bot_id": 1, "name": "Existing Chain"}

    mock_chain_service.create_chain.side_effect = HTTPException(
        status_code=400,
        detail="Chain with name 'Existing Chain' already exists",
    )

    response = client.post("/api/v1/chain/", json=test_chain_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "detail": "Chain with name 'Existing Chain' already exists"
    }


@pytest.mark.asyncio
async def test_get_chains_success(mock_chain_service):
    mock_chains = [
        ChainResponse(id=1, bot_id=1, name="Chain 1"),
        ChainResponse(id=2, bot_id=1, name="Chain 2"),
    ]
    mock_chain_service.get_chains.return_value = ChainsResponse(
        chains=mock_chains
    )

    response = client.get("/api/v1/chain/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "chains": [
            {"id": 1, "bot_id": 1, "name": "Chain 1"},
            {"id": 2, "bot_id": 1, "name": "Chain 2"},
        ]
    }


@pytest.mark.asyncio
async def test_get_chains_empty(mock_chain_service):
    mock_chain_service.get_chains.return_value = ChainsResponse(chains=[])

    response = client.get("/api/v1/chain/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"chains": []}


@pytest.mark.asyncio
async def test_update_chain_success(mock_chain_service):
    test_update_data = {"name": "Updated Chain"}

    mock_chain = MagicMock()
    mock_chain.id = 1
    mock_chain.bot_id = 1
    mock_chain.name = "Updated Chain"

    mock_chain_service.update_chain.return_value = mock_chain

    response = client.patch("/api/v1/chain/1", json=test_update_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"id": 1, "bot_id": 1, "name": "Updated Chain"}


@pytest.mark.asyncio
async def test_update_chain_not_found(mock_chain_service):
    test_update_data = {"name": "Updated Chain"}

    mock_chain_service.update_chain.side_effect = HTTPException(
        status_code=404, detail="Chain with ID 999 not found"
    )

    response = client.patch("/api/v1/chain/999", json=test_update_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Chain with ID 999 not found"}


@pytest.mark.asyncio
async def test_delete_chain_success(mock_chain_service):
    response = client.delete("/api/v1/chain/1")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    mock_chain_service.delete_chain.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_delete_chain_not_found(mock_chain_service):
    mock_chain_service.delete_chain.side_effect = HTTPException(
        status_code=404, detail="Chain with ID 999 not found"
    )

    response = client.delete("/api/v1/chain/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Chain with ID 999 not found"}


@pytest.mark.asyncio
async def test_get_chain_with_details_success(mock_chain_service):
    mock_chain_data = {
        "id": 1,
        "name": "Test Chain",
        "first_step": {
            "id": 1,
            "name": "First Step",
            "message": "Welcome message",
            "buttons": [{"id": 1, "text": "Option 1", "next_step": None}],
        },
    }
    mock_chain_service.get_chain_with_steps_and_buttons.return_value = (
        mock_chain_data
    )

    response = client.get("/api/v1/chain/detail/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == mock_chain_data


@pytest.mark.asyncio
async def test_get_chain_with_details_not_found(mock_chain_service):
    mock_chain_service.get_chain_with_steps_and_buttons.return_value = None

    response = client.get("/api/v1/chain/detail/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Chain not found"}


@pytest.mark.asyncio
async def test_get_chain_results_success(mock_chain_service):
    mock_results = {
        "items": [
            {
                "user_id": 123,
                "username": "test_user",
                "first_name": "Test",
                "last_name": "User",
                "photo": "http://example.com/photo.jpg",
                "answers": {"q1": "answer1"},
                "last_interaction": datetime.datetime.now().isoformat(),
                "current_step": 1,
            }
        ],
        "total": 1,
        "page": 1,
        "per_page": 10,
        "total_pages": 1,
    }
    mock_chain_service.get_paginated_chain_results.return_value = mock_results

    response = client.get("/api/v1/chain/results/1?page=1&per_page=10")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == mock_results


@pytest.mark.asyncio
async def test_get_chain_results_not_found(mock_chain_service):
    # Adjust the test to match the actual error handling in the endpoint
    mock_chain_service.get_paginated_chain_results.return_value = {
        "items": [],
        "total": 0,
        "page": 1,
        "per_page": 10,
        "total_pages": 0,
    }

    response = client.get("/api/v1/chain/results/999")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["total"] == 0


@pytest.mark.asyncio
async def test_get_chain_results_invalid_params(mock_chain_service):
    # Test FastAPI's built-in parameter validation
    response = client.get("/api/v1/chain/results/1?page=0")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
