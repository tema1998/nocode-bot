from typing import Any, List, Optional, Type, Union
from uuid import UUID

# from sqlalchemy.future import select, func
from sqlalchemy import delete, select, update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import joinedload, sessionmaker
from src.db.db_utils import Base
from src.repositories.async_data_repository import AsyncRepository


class PostgresAsyncRepository(AsyncRepository):
    def __init__(self, dsn: str):
        self.engine = create_async_engine(dsn, echo=True)
        self.async_session = sessionmaker(  # type: ignore
            bind=self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def fetch_by_id(
        self, model_class: Type[Base], record_id: str
    ) -> Optional[Base]:
        async with self.async_session() as session:
            result = await session.get(model_class, record_id)
            return result

    async def fetch_by_query(
        self, model_class: Type[Base], column: str, value: Any
    ) -> Union[None, List[Base]]:
        async with self.async_session() as session:
            stmt = select(model_class).where(
                getattr(model_class, column) == value
            )
            result = await session.execute(stmt)
            items = result.scalars().all()
            return items if items else None

    async def fetch_by_query_with_pagination(
        self,
        model_class: Type[Base],
        column: str,
        value: Any,
        skip: int = 0,
        limit: int = 10,
    ) -> Union[None, List[Base]]:
        async with self.async_session() as session:
            stmt = (
                select(model_class)
                .where(getattr(model_class, column) == value)
                .offset(skip)
                .limit(limit)
            )
            result = await session.execute(stmt)
            items = result.scalars().all()
            return items if items else None

    async def fetch_by_query_joinedload(
        self,
        model_class: Type[Base],
        column: str,
        value: Any,
        joinedload_field: str,
    ) -> Union[None, List[Base]]:
        """
        Get
        @param model_class: Model
        @param column: Column for condition.
        @param value: Value for condition.
        @param joinedload_field: Joined field to query.
        @return:
        """
        async with self.async_session() as session:
            stmt = (
                select(model_class)
                .options(joinedload(getattr(model_class, joinedload_field)))
                .where(getattr(model_class, column) == value)
            )
            result = await session.execute(stmt)
            items = result.scalars().unique().all()
            return items if items else None

    async def fetch_all(
        self, model_class: Type[Base]
    ) -> Union[None, List[Base]]:
        async with self.async_session() as session:
            stmt = select(model_class)
            result = await session.execute(stmt)
            items = result.scalars().all()
            return items if items else None

    async def insert(self, obj: Base) -> Any:
        async with self.async_session() as session:
            session.add(obj)
            await session.commit()
            await session.refresh(obj)
            return obj

    async def update(self, obj: Base) -> Any:
        async with self.async_session() as session:
            # Convert the SQLAlchemy ORM object to a dictionary of its fields
            obj_dict = {
                c.name: getattr(obj, c.name) for c in obj.__table__.columns
            }

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

    async def delete(self, model_class: Type[Base], record_id: UUID) -> Any:
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
        self, model_class: Type[Base], ids_list: Any
    ) -> Union[None, List[Base]]:
        async with self.async_session() as session:
            stmt = (
                select(model_class)
                .filter(model_class.id.in_(ids_list))
                .order_by(model_class.created_at.desc())
            )
            result = await session.execute(stmt)
            items = result.scalars().all()
            return items if items else None
