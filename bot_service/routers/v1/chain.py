import logging

from bot_service.models import Chain
from bot_service.schemas.chain import ChainCreate, ChainResponse, ChainUpdate
from bot_service.services.chain_service import ChainService, get_chain_service
from fastapi import APIRouter, Depends, HTTPException
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
    return ChainResponse(
        id=int(created_chain.id),
        bot_id=int(created_chain.bot_id),
        name=str(created_chain.name),
    )


@router.get(
    "/{chain_id}",
    response_model=ChainResponse,
    summary="Get chain details by ID",
    description="Retrieve details of a chain by its ID.",
    response_description="The chain's details.",
    status_code=status.HTTP_200_OK,
)
async def get_chain(
    chain_id: int,
    chain_service: ChainService = Depends(get_chain_service),
) -> ChainResponse:
    """
    Retrieve details of a chain by its ID.

    Args:
        chain_id (int): The ID of the chain to retrieve.
        chain_service (ChainService): The service for bot-related operations.

    Returns:
        ChainResponse: The chain's details.
    """
    chain = await chain_service.get_chain(chain_id)
    return ChainResponse(
        id=int(chain.id),
        bot_id=int(chain.bot_id),
        name=str(chain.name),
    )


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


@router.get("/detail/{chain_id}")
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
        HTTPException: If the chain with the specified ID is not found.
    """
    # Fetch the chain data with all its steps and buttons
    chain_data = await chain_service.get_chain_with_steps_and_buttons(chain_id)

    # If the chain is not found, raise a 404 error
    if not chain_data:
        raise HTTPException(status_code=404, detail="Chain not found")

    # Return the chain data
    return chain_data
