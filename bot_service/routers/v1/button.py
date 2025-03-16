from bot_service.models.main_menu import (
    Button,
)
from bot_service.repositories.async_pg_repository import (
    PostgresAsyncRepository,
    get_repository,
)
from bot_service.schemas.bot import (
    ButtonCreate,
)
from fastapi import APIRouter, Depends


router = APIRouter()


@router.post(
    "/",
    summary="Create a button",
    description="Creates a new button associated with a specific step in a funnel.",
    response_description="The created button object",
    status_code=201,
)
async def create_button(
    button: ButtonCreate,
    repository: PostgresAsyncRepository = Depends(get_repository),
):
    # Create a button object
    db_button = Button(
        step_id=button.step_id,
        text=button.text,
        next_step_id=button.next_step_id,
    )
    # Insert the button into the database
    inserted_button = await repository.insert(db_button)
    return inserted_button
