import logging

from bot_service.core.configs import config
from bot_service.models.chain import Chain
from bot_service.repositories.async_pg_repository import (
    PostgresAsyncRepository,
)
from bot_service.schemas.chain import ChainUpdate
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

    async def get_chain(self, chain_id: int) -> Chain:
        """
        Retrieve a chain by its ID.

        Args:
            chain_id (int): The ID of the chain to retrieve.

        Returns:
            Chain: The retrieved chain.

        Raises:
            HTTPException: If the chain is not found or if there is an error fetching the chain.
        """
        try:
            chain = await self.db_repository.fetch_by_id(Chain, chain_id)
            if chain is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Chain with ID {chain_id} not found",
                )
            return chain  # type: ignore
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to fetch chain: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch chain",
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


async def get_chain_service() -> ChainService:
    """
    Dependency function to get an instance of ChainService.

    Returns:
        ChainService: An instance of ChainService.
    """
    return ChainService(db_repository=PostgresAsyncRepository(dsn=config.dsn))
