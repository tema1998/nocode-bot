import logging

from bot_service.core.configs import config
from bot_service.models.chain import ChainButton, ChainStep
from bot_service.repositories.async_pg_repository import (
    PostgresAsyncRepository,
)
from bot_service.schemas.chain_step import ChainStepCreate, ChainStepUpdate
from fastapi import HTTPException, status


logger = logging.getLogger(__name__)


class ChainStepService:
    """
    Service class for managing chain steps in the database.
    Handles CRUD operations and additional logic for chain steps.
    """

    def __init__(self, db_repository: PostgresAsyncRepository):
        """
        Initialize the ChainStepService with a database repository.

        Args:
            db_repository (PostgresAsyncRepository): The repository for database operations.
        """
        self.db_repository = db_repository

    async def create_chain_step(
        self, chain_step: ChainStepCreate
    ) -> ChainStep:
        """
        Create a new chain step in the database.

        Args:
            chain_step (ChainStepCreate): The data to create the chain step.

        Returns:
            ChainStep: The created chain step.

        Raises:
            HTTPException: If the creation fails or the data is invalid.
        """
        try:
            # Create a new ChainStep instance from the provided data
            db_chain_step = ChainStep(
                chain_id=chain_step.chain_id,
                name=chain_step.name,
                message=chain_step.message,
                next_step_id=chain_step.next_step_id,
                text_input=chain_step.text_input,
            )
            # Insert the new chain step into the database
            created_chain_step = await self.db_repository.insert(db_chain_step)

            if not isinstance(created_chain_step, ChainStep):
                raise ValueError("Unexpected return type from insert method")

            # If the step comes after the button - set this step as the next for the button
            if chain_step.set_as_next_step_for_button_id:
                await self._set_step_as_next_step_for_button(
                    button_id=int(chain_step.set_as_next_step_for_button_id),  # type: ignore
                    next_chain_step_id=int(created_chain_step.id),
                )

        except Exception as e:
            logger.error(f"Failed to create chain step: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create chain step",
            )

        return created_chain_step

    async def get_chain_step(self, chain_step_id: int) -> ChainStep:
        """
        Retrieve a chain step by its ID.

        Args:
            chain_step_id (int): The ID of the chain step to retrieve.

        Returns:
            ChainStep: The retrieved chain step.

        Raises:
            HTTPException: If the chain step is not found or the fetch fails.
        """
        try:
            chain_step = await self.db_repository.fetch_by_id(
                ChainStep, chain_step_id
            )
            if chain_step is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Chain step with ID {chain_step_id} not found",
                )
            return chain_step  # type: ignore
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to fetch chain step: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch chain step",
            )

    async def update_chain_step(
        self, chain_step_id: int, chain_step_update: ChainStepUpdate
    ) -> ChainStep:
        """
        Update an existing chain step.

        Args:
            chain_step_id (int): The ID of the chain step to update.
            chain_step_update (ChainStepUpdate): The data to update the chain step with.

        Returns:
            ChainStep: The updated chain step.

        Raises:
            HTTPException: If the chain step is not found or the update fails.
        """
        try:
            # Fetch the existing chain step
            chain_step = await self.db_repository.fetch_by_id(
                ChainStep, chain_step_id
            )
            if chain_step is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Chain step with ID {chain_step_id} not found",
                )

            # Update the chain step fields if provided
            if chain_step_update.name is not None:
                chain_step.name = chain_step_update.name
            if chain_step_update.message is not None:
                chain_step.message = chain_step_update.message
            if chain_step_update.next_step_id is not None:
                chain_step.next_step_id = chain_step_update.next_step_id
            if chain_step_update.text_input is not None:
                chain_step.text_input = chain_step_update.text_input

            # Save the updated chain step to the database
            await self.db_repository.update(chain_step)
            return chain_step  # type: ignore
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to update chain step: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update chain step",
            )

    async def delete_chain_step(self, chain_step_id: int) -> None:
        """
        Delete a chain step by its ID.

        Args:
            chain_step_id (int): The ID of the chain step to delete.

        Raises:
            HTTPException: If the chain step is not found or the deletion fails.
        """
        try:
            # Fetch the chain step to ensure it exists
            chain_step = await self.db_repository.fetch_by_id(
                ChainStep, chain_step_id
            )
            if chain_step is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Chain step with ID {chain_step_id} not found",
                )

            # Delete the chain step from the database
            await self.db_repository.delete(ChainStep, chain_step_id)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to delete chain step: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete chain step",
            )

    async def _set_step_as_next_step_for_button(
        self, button_id: int, next_chain_step_id: int
    ) -> None:
        """
        Set a chain step as the next step for a button.

        Args:
            button_id (int): The ID of the button.
            next_chain_step_id (int): The ID of the chain step to set as the next step.

        Raises:
            HTTPException: If the button is not found or the update fails.
        """
        try:
            # Fetch the button and update its next_step_id
            button = await self.db_repository.fetch_by_id(
                ChainButton, button_id
            )
            button.next_step_id = next_chain_step_id  # type:ignore
            await self.db_repository.update(button)
        except Exception as e:
            logger.error(
                f"Failed to set step as next step for button: {str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to set step as next step for button",
            )


async def get_chain_step_service() -> ChainStepService:
    """
    Dependency function to get an instance of ChainStepService.

    Returns:
        ChainStepService: An instance of ChainStepService.
    """
    return ChainStepService(
        db_repository=PostgresAsyncRepository(dsn=config.dsn)
    )
