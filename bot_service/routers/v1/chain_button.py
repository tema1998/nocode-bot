from bot_service.schemas.chain_button import (
    ChainButtonCreate,
    ChainButtonResponse,
    ChainButtonUpdate,
)
from bot_service.services.chain_button_service import (
    ChainButtonService,
    get_chain_button_service,
)
from fastapi import APIRouter, Depends
from starlette import status


router = APIRouter()


@router.post(
    "/",
    response_model=ChainButtonResponse,
    summary="Create a new chain button",
    description="Create a new chain button associated with a chain step.",
    response_description="The created chain button details.",
    status_code=status.HTTP_201_CREATED,
)
async def create_chain_button(
    chain_button: ChainButtonCreate,
    chain_button_service: ChainButtonService = Depends(
        get_chain_button_service
    ),
) -> ChainButtonResponse:
    created_chain_button = await chain_button_service.create_chain_button(
        chain_button
    )
    return ChainButtonResponse(
        id=int(created_chain_button.id),
        step_id=int(created_chain_button.step_id),
        text=str(created_chain_button.text),
        callback=(
            str(created_chain_button.callback)
            if created_chain_button.callback
            else None
        ),
        next_step_id=(
            int(created_chain_button.next_step_id)
            if created_chain_button.next_step_id
            else None
        ),
    )


@router.get(
    "/{chain_button_id}",
    response_model=ChainButtonResponse,
    summary="Get chain button details by ID",
    description="Retrieve details of a chain button by its ID.",
    response_description="The chain button's details.",
    status_code=status.HTTP_200_OK,
)
async def get_chain_button(
    chain_button_id: int,
    chain_button_service: ChainButtonService = Depends(
        get_chain_button_service
    ),
) -> ChainButtonResponse:
    chain_button = await chain_button_service.get_chain_button(chain_button_id)
    return ChainButtonResponse(
        id=int(chain_button.id),
        step_id=int(chain_button.step_id),
        text=str(chain_button.text),
        callback=str(chain_button.callback) if chain_button.callback else None,
        next_step_id=(
            int(chain_button.next_step_id)
            if chain_button.next_step_id
            else None
        ),
    )


@router.patch(
    "/{chain_button_id}",
    response_model=ChainButtonResponse,
    summary="Update chain button details by ID",
    description="Update chain button details such as text, callback, and next_step_id.",
    response_description="The updated chain button details.",
    status_code=status.HTTP_200_OK,
)
async def update_chain_button(
    chain_button_id: int,
    chain_button_update: ChainButtonUpdate,
    chain_button_service: ChainButtonService = Depends(
        get_chain_button_service
    ),
) -> ChainButtonResponse:
    updated_chain_button = await chain_button_service.update_chain_button(
        chain_button_id, chain_button_update
    )
    return ChainButtonResponse(
        id=int(updated_chain_button.id),
        step_id=int(updated_chain_button.step_id),
        text=str(updated_chain_button.text),
        callback=(
            str(updated_chain_button.callback)
            if updated_chain_button.callback
            else None
        ),
        next_step_id=(
            int(updated_chain_button.next_step_id)
            if updated_chain_button.next_step_id
            else None
        ),
    )


@router.delete(
    "/{chain_button_id}",
    summary="Delete a chain button by ID",
    description="Delete a chain button by its ID. This operation is irreversible.",
    response_description="Confirmation of the chain button deletion.",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_chain_button(
    chain_button_id: int,
    chain_button_service: ChainButtonService = Depends(
        get_chain_button_service
    ),
) -> None:
    await chain_button_service.delete_chain_button(chain_button_id)
