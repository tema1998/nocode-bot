from bot_service.schemas.chain_step import (
    ChainStepCreate,
    ChainStepResponse,
    ChainStepUpdate,
)
from bot_service.services.chain_step_service import (
    ChainStepService,
    get_chain_step_service,
)
from fastapi import APIRouter, Depends
from starlette import status


router = APIRouter()


@router.post(
    "/",
    response_model=ChainStepResponse,
    summary="Create a new chain step",
    description="Create a new chain step associated with a chain.",
    response_description="The created chain step details.",
    status_code=status.HTTP_201_CREATED,
)
async def create_chain_step(
    chain_step: ChainStepCreate,
    chain_step_service: ChainStepService = Depends(get_chain_step_service),
) -> ChainStepResponse:

    # Create chain step
    created_chain_step = await chain_step_service.create_chain_step(chain_step)

    # Set created step as next step of

    return ChainStepResponse(
        id=int(created_chain_step.id),
        chain_id=int(created_chain_step.chain_id),
        message=str(created_chain_step.message),
        next_step_id=(
            int(created_chain_step.next_step_id)
            if created_chain_step.next_step_id
            else None
        ),
        text_input=bool(created_chain_step.text_input),
    )


@router.get(
    "/{chain_step_id}",
    response_model=ChainStepResponse,
    summary="Get chain step details by ID",
    description="Retrieve details of a chain step by its ID.",
    response_description="The chain step's details.",
    status_code=status.HTTP_200_OK,
)
async def get_chain_step(
    chain_step_id: int,
    chain_step_service: ChainStepService = Depends(get_chain_step_service),
) -> ChainStepResponse:
    chain_step = await chain_step_service.get_chain_step(chain_step_id)
    return ChainStepResponse(
        id=int(chain_step.id),
        chain_id=int(chain_step.chain_id),
        message=str(chain_step.message),
        next_step_id=(
            int(chain_step.next_step_id) if chain_step.next_step_id else None
        ),
        text_input=bool(chain_step.text_input),
    )


@router.patch(
    "/{chain_step_id}",
    response_model=ChainStepResponse,
    summary="Update chain step details by ID",
    description="Update chain step details such as message, next_step_id, and text_input.",
    response_description="The updated chain step details.",
    status_code=status.HTTP_200_OK,
)
async def update_chain_step(
    chain_step_id: int,
    chain_step_update: ChainStepUpdate,
    chain_step_service: ChainStepService = Depends(get_chain_step_service),
) -> ChainStepResponse:
    updated_chain_step = await chain_step_service.update_chain_step(
        chain_step_id, chain_step_update
    )
    return ChainStepResponse(
        id=int(updated_chain_step.id),
        chain_id=int(updated_chain_step.chain_id),
        message=str(updated_chain_step.message),
        next_step_id=(
            int(updated_chain_step.next_step_id)
            if updated_chain_step.next_step_id
            else None
        ),
        text_input=bool(updated_chain_step.text_input),
    )


@router.delete(
    "/{chain_step_id}",
    summary="Delete a chain step by ID",
    description="Delete a chain step by its ID. This operation is irreversible.",
    response_description="Confirmation of the chain step deletion.",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_chain_step(
    chain_step_id: int,
    chain_step_service: ChainStepService = Depends(get_chain_step_service),
) -> None:
    await chain_step_service.delete_chain_step(chain_step_id)
