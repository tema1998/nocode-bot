from datetime import datetime
from typing import Any, Dict, List, Optional, Type, Union
from uuid import UUID

from bot_service.core.configs import config
from bot_service.db.db_utils import Base
from bot_service.repositories.async_data_repository import AsyncDataRepository
from sqlalchemy import and_, delete, func, select, update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import joinedload, sessionmaker


class PostgresAsyncRepository(AsyncDataRepository):
    """Asynchronous repository for performing database operations with PostgreSQL."""

    def __init__(self, dsn: str):
        """
        Initializes the PostgresAsyncRepository with a data source name (DSN).

        Args:
            dsn (str): The data source name for connecting to the PostgreSQL database.
        """
        self.engine = create_async_engine(dsn, echo=True)
        self.async_session = sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,  # type:ignore
        )

    async def fetch_by_id(
        self, model_class: Type[Base], record_id: Union[str, int]
    ) -> Optional[Base]:
        """
        Fetch a record by its ID.

        Args:
            model_class (Type[Base]): The ORM model class to fetch from.
            record_id (Union[str, int]): The ID of the record to fetch.

        Returns:
            Optional[Base]: The fetched record or None if not found.
        """
        async with self.async_session() as session:
            result = await session.get(model_class, record_id)
            return result

    async def fetch_by_id_joinedload(
        self,
        model_class: Type[Base],
        record_id: Union[str, int],
        joinedload_field: Optional[str] = None,
    ) -> Optional[Base]:
        """
        Fetch a record by its ID and optionally join-load related data.

        Args:
            model_class (Type[Base]): The ORM model class to fetch from.
            record_id (Union[str, int]): The ID of the record to fetch.
            joinedload_field (Optional[str]): The field to joined-load (if any).

        Returns:
            Optional[Base]: The fetched record with joined-loaded data or None if not found.
        """
        async with self.async_session() as session:
            stmt = select(model_class).where(model_class.id == record_id)

            if joinedload_field:
                # Apply joinedload option if a field is specified
                stmt = stmt.options(
                    joinedload(getattr(model_class, joinedload_field))
                )

            result = await session.execute(stmt)
            item = result.scalars().first()

            return item

    async def fetch_by_id_joinedload_fields(
        self,
        model_class: Type[Base],
        record_id: Union[str, int],
        joinedload_fields: List[str],
    ) -> Optional[Base]:
        """
        Fetch a record by its ID and optionally join-load related data.

        Args:
            model_class (Type[Base]): The ORM model class to fetch from.
            record_id (Union[str, int]): The ID of the record to fetch.
            joinedload_fields (List[str]): The fields to joined-load (if any).

        Returns:
            Optional[Base]: The fetched record with joined-loaded data or None if not found.
        """
        async with self.async_session() as session:
            stmt = select(model_class).where(model_class.id == record_id)

            if joinedload_fields:
                for field in joinedload_fields:
                    # Разделяем вложенные поля (например, "steps.chain_buttons")
                    parts = field.split(".")
                    current_options = joinedload(
                        getattr(model_class, parts[0])
                    )

                    # Добавляем вложенные joinedload
                    for part in parts[1:]:
                        # Получаем класс связанной модели
                        related_model = getattr(
                            model_class, parts[0]
                        ).property.mapper.class_
                        current_options = current_options.joinedload(
                            getattr(related_model, part)
                        )

                    stmt = stmt.options(current_options)

            result = await session.execute(stmt)
            item = result.scalars().first()

            return item

    async def fetch_by_query(
        self, model_class: Type[Base], filters: Dict[str, Any]
    ) -> Union[None, List[Base]]:
        """
        Fetch multiple records based on a set of filters.

        Args:
            model_class (Type[Base]): The ORM model class to query.
            filters (Dict[str, Any]): A dictionary of filters to apply to the query.

        Returns:
            Union[None, List[Base]]: A list of fetched records or None if none found.
        """
        async with self.async_session() as session:
            conditions = []

            # Build conditions from filters
            for column, value in filters.items():
                conditions.append(getattr(model_class, column) == value)

            stmt = select(model_class).where(and_(*conditions))

            result = await session.execute(stmt)
            items = result.scalars().all()

            return items if items else None

    async def fetch_by_query_one(
        self, model_class: Type[Base], filters: Dict[str, Any]
    ) -> Union[None, Base]:
        """
        Fetch one record based on a set of filters.

        Args:
            model_class (Type[Base]): The ORM model class to query.
            filters (Dict[str, Any]): A dictionary of filters to apply to the query.

        Returns:
            Union[None, Base]: A list of fetched record or None if none found.
        """
        async with self.async_session() as session:
            conditions = []

            # Build conditions from filters
            for column, value in filters.items():
                conditions.append(getattr(model_class, column) == value)

            stmt = select(model_class).where(and_(*conditions))

            result = await session.execute(stmt)
            item = result.scalars().one_or_none()

            return item

    async def fetch_by_query_one_last_updated(
        self, model_class: Type[Base], filters: Dict[str, Any]
    ) -> Union[None, Base]:
        """
        Fetch one record based on a set of filters.

        Args:
            model_class (Type[Base]): The ORM model class to query.
            filters (Dict[str, Any]): A dictionary of filters to apply to the query.

        Returns:
            Union[None, Base]: The fetched record or None if none found.
        """
        async with self.async_session() as session:
            conditions = []

            # Build conditions from filters
            for column, value in filters.items():
                conditions.append(getattr(model_class, column) == value)

            stmt = (
                select(model_class)
                .where(and_(*conditions))
                .order_by(model_class.updated_at.desc())
                .limit(1)
            )

            result = await session.execute(stmt)
            item = result.scalars().one_or_none()

            return item

    async def fetch_by_query_one_joinedload(
        self,
        model_class: Type[Base],
        filters: Dict[str, Any],
        joinedload_field: Optional[str] = None,
    ) -> Union[None, Base]:
        """
        Fetch one record based on a set of filters.

        Args:
            model_class (Type[Base]): The ORM model class to query.
            filters (Dict[str, Any]): A dictionary of filters to apply to the query.
            joinedload_field (Optional[str]): The field foe join operation.
        Returns:
            Union[None, Base]: A list of fetched record or None if none found.
        """
        async with self.async_session() as session:
            conditions = []

            # Build conditions from filters
            for column, value in filters.items():
                conditions.append(getattr(model_class, column) == value)

            stmt = select(model_class).where(and_(*conditions))

            if joinedload_field:
                # Apply joinedload option if a field is specified
                stmt = stmt.options(
                    joinedload(getattr(model_class, joinedload_field))
                )

            result = await session.execute(stmt)
            item = result.scalars().unique().one_or_none()

            return item

    async def fetch_by_query_with_pagination(
        self,
        model_class: Type[Base],
        column: str,
        value: Any,
        skip: int = 0,
        limit: int = 10,
        order_by_column: Optional[str] = None,
        descending: bool = False,
    ) -> Union[None, List[Base]]:
        """
        Fetch records based on filters with pagination support.

        Args:
            model_class (Type[Base]): The ORM model class to query.
            column (str): The column to filter by.
            value (Any): The value to filter against.
            skip (int): Number of records to skip (for pagination).
            limit (int): Maximum number of records to return.
            order_by_column (Optional[str]): Column to order by. If None, no ordering is applied.
            descending (bool): If True, sort in descending order.
        Returns:
            Union[None, List[Base]]: A list of fetched records or None if none found.
        """
        async with self.async_session() as session:
            stmt = select(model_class).where(
                getattr(model_class, column) == value
            )

            if order_by_column:
                column_to_order = getattr(model_class, order_by_column)
                if descending:
                    stmt = stmt.order_by(column_to_order.desc())
                else:
                    stmt = stmt.order_by(column_to_order.asc())

            stmt = stmt.offset(skip).limit(limit)
            result = await session.execute(stmt)
            items = result.scalars().all()
            return items if items else None

    async def fetch_by_query_joinedload(
        self,
        model_class: Type[Base],
        filters: Dict[str, Any],
        joinedload_fields: List[str],
    ) -> Union[None, List[Base]]:
        """
        Fetch records based on filters and join-load specified fields.

        Args:
            model_class (Type[Base]): The ORM model class to query.
            filters (Dict[str, Any]): A dictionary of filters to apply to the query.
            joinedload_fields (List[str]): List of fields to joined-load.

        Returns:
            Union[None, List[Base]]: A list of fetched records with joined-loaded data or None if none found.
        """
        async with self.async_session() as session:
            stmt = select(model_class)

            # Add joinedload for each specified field
            for field in joinedload_fields:
                stmt = stmt.options(joinedload(getattr(model_class, field)))

            conditions = []
            for column, value in filters.items():
                condition = getattr(model_class, column) == value
                conditions.append(condition)

            # Apply conditions to the query
            if conditions:
                stmt = stmt.where(and_(*conditions))

            result = await session.execute(stmt)
            items = result.scalars().unique().all()

            return items if items else None

    async def fetch_all(
        self, model_class: Type[Base]
    ) -> Union[None, List[Base]]:
        """
        Fetch all records for a given model.

        Args:
            model_class (Type[Base]): The ORM model class to fetch records from.

        Returns:
            Union[None, List[Base]]: A list of all fetched records or None if none found.
        """
        async with self.async_session() as session:
            stmt = select(model_class)
            result = await session.execute(stmt)
            items = result.scalars().all()
            return items if items else None

    async def insert(self, obj: Base) -> Any:
        """
        Insert a new record into the database.

        Args:
            obj (Base): The object to insert into the database.

        Returns:
            Any: The inserted object with updated fields (e.g., ID).
        """
        async with self.async_session() as session:
            session.add(obj)  # Add the object to the session
            await session.commit()  # Commit the transaction
            await session.refresh(
                obj
            )  # Refresh the object to get its updated state
            return obj

    async def update(self, obj: Base) -> Any:
        """
        Update an existing record in the database.

        Args:
            obj (Base): The object with updated fields to be saved.

        Returns:
            Any: The updated object.

        Raises:
            NoResultFound: If no object is found with the given ID.
        """
        async with self.async_session() as session:
            # Convert the SQLAlchemy ORM object to a dictionary of its fields
            obj_dict = {
                c.name: getattr(obj, c.name) for c in obj.__table__.columns
            }

            if "updated_at" in obj_dict:
                obj_dict["updated_at"] = datetime.now()

            stmt = (
                update(obj.__class__)
                .where(obj.__class__.id == obj.id)
                .values(**obj_dict)
                .execution_options(synchronize_session="fetch")
                .returning(obj.__class__)
            )
            result = await session.execute(stmt)
            await session.commit()

            # Fetch the updated record
            updated_record = result.scalar()
            if updated_record is None:
                raise NoResultFound(
                    f"No {obj.__class__.__name__} found with id: {obj.id}"
                )

            return updated_record

    async def delete(
        self, model_class: Type[Base], record_id: Union[str, int, UUID]
    ) -> Any:
        """
        Delete a record from the database by its ID.

        Args:
            model_class (Type[Base]): The ORM model class to delete from.
            record_id (Union[str, int, UUID]): The ID of the record to delete.

        Returns:
            Any: The deleted record if successful.
        """
        async with self.async_session() as session:
            stmt = (
                delete(model_class)
                .where(model_class.id == record_id)
                .returning(model_class)
            )
            result = await session.execute(stmt)
            await session.commit()
            return result.scalar()

    async def fetch_by_id_list_order_by(
        self, model_class: Type[Base], ids_list: List[Union[str, int]]
    ) -> Union[None, List[Base]]:
        """
        Fetch records by a list of IDs, ordered by creation date.

        Args:
            model_class (Type[Base]): The ORM model class to query records from.
            ids_list (List[Union[str, int]]): The list of IDs to filter by.

        Returns:
            Union[None, List[Base]]: A list of fetched records ordered by creation date or None if none found.
        """
        async with self.async_session() as session:
            stmt = (
                select(model_class)
                .filter(model_class.id.in_(ids_list))
                .order_by(model_class.created_at.desc())
            )
            result = await session.execute(stmt)
            items = result.scalars().all()
            return items if items else None

    async def count_by_query(
        self, model_class: Type[Base], column: str, value: Any
    ) -> int:
        """
        Count records matching the specified filter condition.

        Args:
            model_class: The SQLAlchemy model class to query
            column: Name of the column to filter by
            value: Value to match in the specified column

        Returns:
            int: Count of matching records (0 if none found)
        """
        async with self.async_session() as session:
            # Build count query
            stmt = (
                select(func.count())
                .select_from(model_class)
                .where(getattr(model_class, column) == value)
            )

            # Execute and return scalar result
            result = await session.execute(stmt)
            return result.scalar_one() or 0


async def get_repository() -> PostgresAsyncRepository:
    """Dependency function to get the PostgresAsyncRepository instance."""
    repository = PostgresAsyncRepository(dsn=config.dsn)
    return repository
