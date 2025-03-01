from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, Union
from uuid import UUID

from bot_service.db.db_utils import Base


class AsyncRepository(ABC):
    @abstractmethod
    async def fetch_by_id(self, model_class, record_id: str) -> Optional[Any]:
        """Fetch a record by its ID from the specified index (e.g., table, collection)."""
        pass

    async def fetch_by_id_joinedload(
        self,
        model_class: Type[Base],
        record_id: str | int,
        joinedload_field: Optional[str] = None,
    ) -> Optional[Base]:
        """Fetch a record by its ID from the specified index (e.g., table, collection), add joined load to query."""
        pass

    @abstractmethod
    async def fetch_by_query(
        self, model_class: Type[Base], filters: Dict[str, Any]
    ) -> Union[None, List[Base]]:
        """Fetch records based on a query from the specified indices (e.g., table, collection)."""
        pass

    async def fetch_by_query_joinedload(
        self,
        model_class: Type[Base],
        filters: Dict[str, Any],
        joinedload_fields: List[str],  # Список полей для joinedload
    ) -> Union[None, List[Base]]:
        """Fetch records based on a query from the specified indices (e.g., table, collection), add joined load."""
        pass

    @abstractmethod
    async def fetch_by_query_with_pagination(
        self, model_class, column: str, value: Any, skip: int, limit: int
    ) -> Optional[List[Any]]:
        """Fetch records based on a query from the specified index (e.g., table, collection) using pagination."""
        pass

    @abstractmethod
    async def fetch_all(self, model_class) -> Optional[List[Any]]:
        """Fetch all records from the specified index (e.g., table, collection)."""
        pass

    @abstractmethod
    async def insert(self, obj) -> Any:
        """Insert a new record into the specified index (e.g., table, collection)."""
        pass

    @abstractmethod
    async def update(self, obj) -> Any:
        """Update an existing record by its ID in the specified index (e.g., table, collection)."""
        pass

    @abstractmethod
    async def delete(self, model_class: Type[Base], record_id: UUID) -> Any:
        """Delete a record by its ID from the specified index (e.g., table, collection)."""
        pass
