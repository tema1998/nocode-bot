import logging

from bot_service.core.configs import config
from bot_service.models.chain import ChainButton
from bot_service.repositories.async_pg_repository import (
    PostgresAsyncRepository,
)
from bot_service.schemas.chain_button import (
    ChainButtonCreate,
    ChainButtonUpdate,
)
from fastapi import HTTPException, status


logger = logging.getLogger(__name__)


class ChainButtonService:
    """
    Service class for managing chain buttons in the database.
    Handles CRUD operations and additional logic for chain buttons.
    """

    def __init__(self, db_repository: PostgresAsyncRepository):
        """
        Initialize the ChainButtonService with a database repository.

        Args:
            db_repository (PostgresAsyncRepository): The repository for database operations.
        """
        self.db_repository = db_repository

    async def create_chain_button(
        self, chain_button: ChainButtonCreate
    ) -> ChainButton:
        """
        Create a new chain button in the database.

        Args:
            chain_button (ChainButtonCreate): The data to create the chain button.

        Returns:
            ChainButton: The created chain button.

        Raises:
            HTTPException: If the creation fails or the data is invalid.
        """
        try:
            # Create a new ChainButton instance from the provided data
            db_chain_button = ChainButton(
                step_id=chain_button.step_id,
                text=chain_button.text,
                callback=chain_button.callback,
            )
            # Insert the new chain button into the database
            created_chain_button = await self.db_repository.insert(
                db_chain_button
            )
            if not isinstance(created_chain_button, ChainButton):
                raise ValueError("Unexpected return type from insert method")
            return created_chain_button
        except Exception as e:
            logger.error(f"Failed to create chain button: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create chain button",
            )

    async def get_chain_button(self, chain_button_id: int) -> ChainButton:
        """
        Retrieve a chain button by its ID.

        Args:
            chain_button_id (int): The ID of the chain button to retrieve.

        Returns:
            ChainButton: The retrieved chain button.

        Raises:
            HTTPException: If the chain button is not found or the fetch fails.
        """
        try:
            chain_button = await self.db_repository.fetch_by_id(
                ChainButton, chain_button_id
            )
            if chain_button is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Chain button with ID {chain_button_id} not found",
                )
            return chain_button  # type: ignore
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to fetch chain button: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch chain button",
            )

    async def update_chain_button(
        self, chain_button_id: int, chain_button_update: ChainButtonUpdate
    ) -> ChainButton:
        """
        Update an existing chain button.

        Args:
            chain_button_id (int): The ID of the chain button to update.
            chain_button_update (ChainButtonUpdate): The data to update the chain button with.

        Returns:
            ChainButton: The updated chain button.

        Raises:
            HTTPException: If the chain button is not found or the update fails.
        """
        try:
            # Fetch the existing chain button
            chain_button = await self.db_repository.fetch_by_id(
                ChainButton, chain_button_id
            )
            if chain_button is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Chain button with ID {chain_button_id} not found",
                )

            # Update the chain button fields if provided
            if chain_button_update.text is not None:
                chain_button.text = chain_button_update.text
            if chain_button_update.callback is not None:
                chain_button.callback = chain_button_update.callback
            if chain_button_update.next_step_id is not None:
                chain_button.next_step_id = chain_button_update.next_step_id

            # Save the updated chain button to the database
            await self.db_repository.update(chain_button)
            return chain_button  # type: ignore
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to update chain button: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update chain button",
            )

    async def delete_chain_button(self, chain_button_id: int) -> None:
        """
        Delete a chain button by its ID.

        Args:
            chain_button_id (int): The ID of the chain button to delete.

        Raises:
            HTTPException: If the chain button is not found or the deletion fails.
        """
        try:
            # Fetch the chain button to ensure it exists
            chain_button = await self.db_repository.fetch_by_id(
                ChainButton, chain_button_id
            )
            if chain_button is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Chain button with ID {chain_button_id} not found",
                )

            # Delete the chain button from the database
            await self.db_repository.delete(ChainButton, chain_button_id)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to delete chain button: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete chain button",
            )

    async def set_next_chain_step_to_button(
        self, button_id: int, next_chain_step_id: int
    ) -> None:
        """
        Set the next chain step for a button.

        Args:
            button_id (int): The ID of the button to update.
            next_chain_step_id (int): The ID of the chain step to set as the next step.

        Raises:
            HTTPException: If the operation fails due to an internal error.
        """
        try:
            # Call the internal method to update the button's next_step_id
            await self._set_next_step_for_button(
                button_id=int(button_id),  # Ensure button_id is an integer
                next_chain_step_id=int(
                    next_chain_step_id
                ),  # Ensure next_chain_step_id is an integer
            )
        except HTTPException:
            # Re-raise HTTPException if it was raised in the internal method
            raise
        except Exception as e:
            # Log the error and raise a 500 Internal Server Error for unexpected failures
            logger.error(f"Failed to set next chain step to button: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to set next chain step to button.",
            )

    async def _set_next_step_for_button(
        self, button_id: int, next_chain_step_id: int
    ) -> None:
        """
        Internal method to update the next_step_id for a button.

        Args:
            button_id (int): The ID of the button to update.
            next_chain_step_id (int): The ID of the chain step to set as the next step.

        Raises:
            HTTPException: If the button is not found, or if the next step is invalid.
        """
        try:
            # Fetch the button from the database
            button = await self.db_repository.fetch_by_id(
                ChainButton, button_id
            )
            if button is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Button with ID {button_id} not found.",
                )

            # Prevent setting the current step as the next step (infinite loop)
            if button.step_id == next_chain_step_id:
                logger.error(
                    f"Cannot set current step as next step. "
                    f"step_id = {button.step_id}, button_id = {button.id}, "
                    f"next_chain_step_id = {next_chain_step_id}"
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot set the current step as the next step.",
                )

            # Update the button's next_step_id
            button.next_step_id = next_chain_step_id  # type: ignore
            await self.db_repository.update(button)

        except HTTPException:
            # Re-raise HTTPException if it was raised in this method
            raise
        except Exception as e:
            # Log the error and raise a 500 Internal Server Error for unexpected failures
            logger.error(f"Failed to set next step for button: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to set next step for button.",
            )


async def get_chain_button_service() -> ChainButtonService:
    """
    Dependency function to get an instance of ChainButtonService.

    Returns:
        ChainButtonService: An instance of ChainButtonService.
    """
    return ChainButtonService(
        db_repository=PostgresAsyncRepository(dsn=config.dsn)
    )
