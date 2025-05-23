import logging
from typing import Any, Dict

from bot_service.models import Chain
from bot_service.schemas.chain import (
    ChainCreate,
    ChainResponse,
    ChainResultsResponse,
    ChainsResponse,
    ChainUpdate,
)
from bot_service.services.chain_service import ChainService, get_chain_service
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from starlette import status


router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/",
    response_model=ChainResponse,
    summary="Create a new chain",
    description="Create a new chain associated with a bot.",
    response_description="The created chain details.",
    status_code=status.HTTP_201_CREATED,
)
async def create_chain(
    chain: ChainCreate,
    chain_service: ChainService = Depends(get_chain_service),
) -> ChainResponse:
    """
    Create a new chain.

    Args:
        chain (ChainCreate): The data to create the chain with.
        chain_service (ChainService): The service for bot-related operations.

    Returns:
        ChainResponse: The created chain details.
    """
    db_chain = Chain(bot_id=chain.bot_id, name=chain.name)
    created_chain = await chain_service.create_chain(db_chain)

    # Create and set first chain's step
    await chain_service.create_and_set_first_step(int(created_chain.id))

    return ChainResponse(
        id=int(created_chain.id),
        bot_id=int(created_chain.bot_id),
        name=str(created_chain.name),
    )


@router.get(
    "/{bot_id}",
    response_model=ChainsResponse,
    summary="Get chains by bot's ID",
    description="Retrieve chains by bot's ID.",
    response_description="The list of chains.",
    status_code=status.HTTP_200_OK,
)
async def get_chains(
    bot_id: int,
    chain_service: ChainService = Depends(get_chain_service),
) -> ChainsResponse:
    """
    Retrieve chains associated with a specific bot ID.

    This endpoint allows you to fetch all chains that belong to the specified
    bot by its unique identifier. The chains are returned as a list within
    the ChainsResponse model.

    Parameters:
    - bot_id (int): The unique identifier for the bot whose chains are to be retrieved.
    - chain_service (ChainService): A dependency providing chain-related services
      (automatically injected by FastAPI).

    Returns:
    ChainsResponse: A response object containing a list of ChainResponse
    objects, representing the chains associated with the specified bot ID.

    Raises:
    HTTPException: If no chains are found for the given bot ID, a 404 status
    (Not Found) will be raised.
    """
    chains = await chain_service.get_chains(bot_id)
    return chains


@router.patch(
    "/{chain_id}",
    response_model=ChainResponse,
    summary="Update chain details by ID",
    description="Update chain details such as name.",
    response_description="The updated chain details.",
    status_code=status.HTTP_200_OK,
)
async def update_chain(
    chain_id: int,
    chain_update: ChainUpdate,
    chain_service: ChainService = Depends(get_chain_service),
) -> ChainResponse:
    """
    Update chain details by ID.

    Args:
        chain_id (int): The ID of the chain to update.
        chain_update (ChainUpdate): The data to update the chain with.
        chain_service (ChainService): The service for bot-related operations.

    Returns:
        ChainResponse: The updated chain details.
    """
    updated_chain = await chain_service.update_chain(chain_id, chain_update)
    return ChainResponse(
        id=int(updated_chain.id),
        bot_id=int(updated_chain.bot_id),
        name=str(updated_chain.name),
    )


@router.delete(
    "/{chain_id}",
    summary="Delete a chain by ID",
    description="Delete a chain by its ID. This operation is irreversible.",
    response_description="Confirmation of the chain deletion.",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_chain(
    chain_id: int,
    chain_service: ChainService = Depends(get_chain_service),
) -> None:
    """
    Delete a chain by its ID.

    Args:
        chain_id (int): The ID of the chain to delete.
        chain_service (ChainService): The service for bot-related operations.

    Returns:
        None: Returns no content on successful deletion.
    """
    await chain_service.delete_chain(chain_id)


@router.get(
    "/detail/{chain_id}",
    summary="Get full chain structure with steps and buttons",
    description="Retrieves a complete chain including all steps and their associated buttons. "
    "Provides the hierarchical structure needed for chain visualization and navigation.",
    response_description="Chain object with nested steps and buttons data",
    status_code=200,
)
async def get_chain_with_details(
    chain_id: int,
    chain_service: ChainService = Depends(get_chain_service),
):
    """
    Retrieve a chain with all its steps and buttons by its ID.

    Args:
        chain_id (int): The ID of the chain to retrieve.
        chain_service (ChainService): The service to handle chain-related operations.

    Returns:
        Dict: A dictionary containing the chain data with all its steps and buttons.

    Raises:
        HTTPException: If the chain with the specified ID is not found (404).
    """
    chain_data = await chain_service.get_chain_with_steps_and_buttons(chain_id)
    if not chain_data:
        raise HTTPException(status_code=404, detail="Chain not found")
    return chain_data


@router.get(
    "/results/{chain_id}",
    summary="Get paginated chain completion results",
    response_model=ChainResultsResponse,
    responses={
        200: {"description": "Successfully retrieved results (may be empty)"},
        400: {"description": "Invalid request parameters"},
        500: {"description": "Internal server error"},
    },
)
async def get_chain_results(
    chain_id: int = Path(
        ..., description="ID of the chain", examples=[1, 2, 3], gt=0
    ),
    page: int = Query(
        1, ge=1, description="Page number starting from 1", examples=[1, 2]
    ),
    per_page: int = Query(
        10,
        ge=1,
        le=100,
        description="Items per page (max 100)",
        examples=[10, 25, 50],
    ),
    chain_service: ChainService = Depends(get_chain_service),
) -> Dict[str, Any]:
    """
    Retrieve paginated completion results for a chain with user details.

    Key features:
    - Always returns 200 status with consistent pagination structure
    - Returns empty items list when no results found
    - Includes complete pagination metadata

    Response includes:
    - items: List of results (maybe empty)
    - total: Total number of results
    - page: Current page number
    - per_page: Items per page
    - total_pages: Total number of pages

    Each item contains:
    - Profile information (name, username, photo)
    - Answers to chain questions
    - Interaction timestamps
    - Current progress status
    """
    try:
        return await chain_service.get_paginated_chain_results(
            chain_id=chain_id, page=page, per_page=per_page
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(
            f"Unexpected error fetching results for chain {chain_id}: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail="Internal server error")
