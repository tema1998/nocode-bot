from bot_service.models.bot import (
    Command,
)
from bot_service.repositories.async_pg_repository import (
    PostgresAsyncRepository,
    get_repository,
)
from bot_service.schemas.bot import (
    CommandCreate,
)
from fastapi import APIRouter, Depends


router = APIRouter()


@router.post(
    "/",
    summary="Add a command to a bot",
    description="Creates a new command associated with a bot in the database.",
    response_description="The created command object",
    status_code=201,
)
async def add_command(
    command: CommandCreate,
    repository: PostgresAsyncRepository = Depends(get_repository),
):
    # Create a command object
    db_command = Command(
        command=command.command,
        response=command.response,
        bot_id=command.bot_id,
    )
    # Insert the command into the database
    inserted_command = await repository.insert(db_command)
    return inserted_command
