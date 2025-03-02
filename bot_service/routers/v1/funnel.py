from bot_service.models.bot import (
    Funnel,
    FunnelStep,
)
from bot_service.repositories.async_pg_repository import (
    PostgresAsyncRepository,
    get_repository,
)
from bot_service.schemas.bot import (
    FunnelCreate,
    FunnelStepCreate,
)
from fastapi import APIRouter, Depends


router = APIRouter()


@router.post(
    "/",
    summary="Create a new funnel",
    description="Creates a new funnel associated with a bot in the database.",
    response_description="The created funnel object",
    status_code=201,
)
async def create_funnel(
    funnel: FunnelCreate,
    repository: PostgresAsyncRepository = Depends(get_repository),
):
    # Create a funnel in the database
    db_funnel = Funnel(name=funnel.name, bot_id=funnel.bot_id)
    inserted_funnel = await repository.insert(db_funnel)
    return inserted_funnel


@router.post(
    "/{funnel_id}/steps/",
    summary="Add a step to a funnel",
    description="Creates a new step associated with a specific funnel in the database.",
    response_description="The created funnel step object",
    status_code=201,
)
async def add_funnel_step(
    funnel_id: int,
    step: FunnelStepCreate,
    repository: PostgresAsyncRepository = Depends(get_repository),
):
    # Create a funnel step object
    db_step = FunnelStep(funnel_id=funnel_id, text=step.text)
    # Insert the funnel step into the database
    inserted_step = await repository.insert(db_step)
    return inserted_step
