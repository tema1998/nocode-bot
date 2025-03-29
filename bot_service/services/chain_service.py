import logging
from typing import Dict, Optional

from bot_service.core.configs import config
from bot_service.models.chain import Chain, ChainButton, ChainStep
from bot_service.repositories.async_pg_repository import (
    PostgresAsyncRepository,
)
from bot_service.schemas.chain import (
    ChainResponse,
    ChainsResponse,
    ChainUpdate,
)
from fastapi import HTTPException, status


logger = logging.getLogger(__name__)


class ChainService:
    def __init__(self, db_repository: PostgresAsyncRepository):
        """
        Initialize the ChainService with a database repository.

        Args:
            db_repository (PostgresAsyncRepository): The repository for database operations.
        """
        self.db_repository = db_repository

    async def create_chain(self, chain: Chain) -> Chain:
        """
        Create a new chain.

        Args:
            chain (Chain): The chain to create.

        Returns:
            Chain: The created chain.

        Raises:
            HTTPException: If the chain name already exists or if there is an error creating the chain.
        """
        try:
            # Check for uniqueness of the chain name
            existing_chain = await self.db_repository.fetch_by_query_one(
                Chain, {"name": chain.name}
            )
            if existing_chain:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Chain with name '{chain.name}' already exists",
                )

            # Insert the new chain
            created_chain = await self.db_repository.insert(chain)
            if not isinstance(created_chain, Chain):
                raise ValueError("Unexpected return type from insert method")
            return created_chain
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to create chain: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create chain",
            )

    async def get_chains(self, bot_id: int) -> ChainsResponse:
        """
        Fetch chains associated with a specific bot ID from the database.

        This asynchronous method queries the database for chains linked to the
        specified bot identifier. If chains are found, it converts them into
        ChainResponse objects, which are then wrapped into a ChainsResponse
        object before being returned.

        Parameters:
        - bot_id (int): The unique identifier for the bot whose chains are to be retrieved.

        Returns:
        ChainsResponse: A response object containing a list of ChainResponse
        objects, representing the chains associated with the specified bot ID.

        Raises:
        HTTPException:
            - If no chains are found or if there is an error during the
              fetching process, an internal server error (500) is raised.
        """
        try:
            chains = await self.db_repository.fetch_by_query(
                Chain, {"bot_id": bot_id}
            )
            chain_responses = (
                [ChainResponse.model_validate(chain) for chain in chains]
                if chains
                else []
            )

            # Return the wrapped response with chains
            return ChainsResponse(chains=chain_responses)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to fetch chains: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch chains",
            )

    async def update_chain(
        self, chain_id: int, chain_update: ChainUpdate
    ) -> Chain:
        """
        Update a chain by its ID.

        Args:
            chain_id (int): The ID of the chain to update.
            chain_update (ChainUpdate): The data to update the chain with.

        Returns:
            Chain: The updated chain.

        Raises:
            HTTPException: If the chain is not found, if the new name already exists,
                          or if there is an error updating the chain.
        """
        try:
            chain = await self.db_repository.fetch_by_id(Chain, chain_id)
            if chain is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Chain with ID {chain_id} not found",
                )

            # Check for uniqueness of the new name (if it has changed)
            if (
                chain_update.name is not None
                and chain_update.name != chain.name
            ):
                existing_chain = await self.db_repository.fetch_by_query_one(
                    Chain, {"name": chain_update.name}
                )
                if existing_chain:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Chain with name '{chain_update.name}' already exists",
                    )

            # Update the chain data
            if chain_update.name is not None:
                chain.name = chain_update.name

            if chain_update.first_chain_step_id is not None:
                chain.first_chain_step_id = chain_update.first_chain_step_id

            await self.db_repository.update(chain)
            return chain  # type: ignore
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to update chain: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update chain",
            )

    async def delete_chain(self, chain_id: int) -> None:
        """
        Delete a chain by its ID.

        Args:
            chain_id (int): The ID of the chain to delete.

        Raises:
            HTTPException: If the chain is not found or if there is an error during deletion.
        """
        try:
            chain = await self.db_repository.fetch_by_id(Chain, chain_id)
            if chain is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Chain with ID {chain_id} not found",
                )

            await self.db_repository.delete(Chain, chain_id)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to delete chain: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete chain",
            )

    async def get_chain_with_steps_and_buttons(
        self, chain_id: int
    ) -> Optional[Dict]:
        """
        Retrieve a chain with all its steps and buttons.

        Args:
            chain_id (int): The ID of the chain to retrieve.

        Returns:
            Optional[Dict]: A dictionary containing the chain data with steps and buttons,
                            or None if the chain is not found.
        """
        # Fetch the chain
        chain = await self.db_repository.fetch_by_id(Chain, chain_id)
        if not chain:
            return None

        # Fetch the first step of the chain
        first_step = await self.db_repository.fetch_by_id(
            ChainStep, chain.first_chain_step_id
        )
        if not first_step:
            return {"id": chain.id, "name": chain.name, "first_step": None}

        # Recursively build the step structure
        first_step_data = await self._build_step(first_step)

        # Return the chain data
        return {
            "id": chain.id,
            "name": chain.name,
            "first_step": first_step_data,
        }

    async def _build_step(self, step: ChainStep) -> Optional[Dict]:
        """
        Recursively build the structure of a step with its buttons and next steps.

        Args:
            step (ChainStep): The current step.

        Returns:
            Optional[Dict]: A dictionary containing the step data with buttons and next steps,
                            or None if the step does not exist.
        """
        if not step:
            return None

        # Fetch buttons for the current step
        buttons = await self.db_repository.fetch_by_query(
            ChainButton, {"step_id": step.id}
        )
        if not buttons:
            buttons = []

        # Recursively build data for each button
        buttons_data = []
        for button in buttons:
            next_step = await self.db_repository.fetch_by_id(
                ChainStep, button.next_step_id
            )
            buttons_data.append(
                {
                    "id": button.id,
                    "text": button.text,
                    "callback": button.callback,
                    "next_step": (
                        await self._build_step(next_step)
                        if next_step
                        else None
                    ),
                }
            )

        # Fetch the next step if it exists
        if step.next_step_id:
            next_step = await self.db_repository.fetch_by_id(
                ChainStep, int(step.next_step_id)
            )
        else:
            next_step = None

        return {
            "id": step.id,
            "name": step.name,
            "message": step.message,
            "next_step": (
                await self._build_step(next_step) if next_step else None
            ),
            "text_input": step.text_input,
            "buttons": buttons_data,
        }

    async def create_and_set_first_step(self, chain_id: int) -> Chain:
        """
        Create and set first chain's step by chain's ID.

        Args:
            chain_id (int): The ID of the chain to set first step.

        Returns:
            Chain: The updated chain.

        Raises:
            HTTPException: If the chain is not found.
        """
        try:
            chain = await self.db_repository.fetch_by_id(Chain, chain_id)
            if chain is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Chain with ID {chain_id} not found",
                )

            # Create first step for chain
            first_step_for_chain = ChainStep(
                name="Первый шаг", message="Начало цепочки", chain_id=chain_id
            )
            created_first_step_for_chain = await self.db_repository.insert(
                first_step_for_chain
            )
            # Set first step for chain
            chain.first_chain_step_id = created_first_step_for_chain.id
            await self.db_repository.update(chain)

            return chain  # type: ignore
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to set first chain's step: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to set first chain's step.",
            )


async def get_chain_service() -> ChainService:
    """
    Dependency function to get an instance of ChainService.

    Returns:
        ChainService: An instance of ChainService.
    """
    return ChainService(db_repository=PostgresAsyncRepository(dsn=config.dsn))
