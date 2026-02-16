from typing import Type, Any, Dict, List, Optional, Union, Tuple

from sqlalchemy import select, update, delete, insert, or_, exists
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.sql import func, Select


class CRUDMixin:
    @classmethod
    def __build_conditions(cls: Type["Base"], filters: dict[str, Any]) -> list:
        conditions = []

        for key, value in filters.items():
            if "__" in key:
                field_name, *lookups = key.rsplit("__", 1)
                lookup = lookups[0]
                case_insensitive = "ic" in lookups

                field = getattr(cls, field_name)

                if lookup == "in":
                    values = list(value)
                    if None in values:
                        values_without_none = [v for v in values if v is not None]
                        if values_without_none:
                            conditions.append(or_(field.in_(values_without_none), field.is_(None)))
                        else:
                            conditions.append(field.is_(None))
                    else:
                        conditions.append(field.in_(value))
                elif lookup == "before":
                    conditions.append(field < value)
                elif lookup == "after":
                    conditions.append(field > value)
                elif lookup == "has":
                    operator = field.ilike if case_insensitive else field.like
                    conditions.append(operator(f"%{value}%"))
                elif lookup == "startswith":
                    operator = field.ilike if case_insensitive else field.like
                    conditions.append(operator(f"{value}%"))
                elif lookup == "endswith":
                    operator = field.ilike if case_insensitive else field.like
                    conditions.append(operator(f"%{value}"))
                else:
                    raise ValueError(f"Unsupported lookup: {lookup}")
            else:
                field = getattr(cls, key)
                conditions.append(field == value)

        return conditions

    @classmethod
    def __build_query(
            cls: Type["Base"], filters: dict[str, Any] | None = None, or_filters: dict[str, Any] | None = None,
            order_by: Union[str, List[str], None] = None, limit: Optional[int] = None
    ) -> Select:
        filters = filters or {}

        conditions = cls.__build_conditions(filters)

        if or_filters:
            or_conditions  = cls.__build_conditions(or_filters)
            conditions.append(or_(*or_conditions))
        print("--------------", *conditions)
        query = select(cls).where(*conditions)

        if order_by:
            if isinstance(order_by, str):
                query = query.order_by(getattr(cls, order_by))
            elif isinstance(order_by, list):
                query = query.order_by(*[getattr(cls, field) for field in order_by])

        if limit is not None:
            query = query.limit(limit)

        return query

    @classmethod
    def __find_with_related(
            cls: Type["Base"], related: Union[Type["Base"], List[Type["Base"]]], strategy: str = "select",
            self_filters: dict | None = None, related_filters: dict | None = None,
    ) -> Select:
        if not isinstance(related, list):
            related = [related]

        self_filters = self_filters or {}
        related_filters = related_filters or {}

        query = select(cls)

        for model in related:
            relationship_attr = None

            for rel in cls.__mapper__.relationships:
                if rel.mapper.class_ == model:
                    relationship_attr = rel.key
                    break

            if not relationship_attr:
                raise ValueError(
                    f"Cannot find relationship from {cls.__name__} to {model.__name__}"
                )

            if strategy == "select":
                query = query.options(joinedload(getattr(cls, relationship_attr)))

                if related_filters:
                    query = query.join(getattr(cls, relationship_attr))

            elif strategy == "prefetch":
                query = query.options(selectinload(getattr(cls, relationship_attr)))

            else:
                raise ValueError(f"Unknown strategy: {strategy}")

            if related_filters:
                related_conditions = model.__build_conditions(related_filters)
                query = query.where(*related_conditions)

        if self_filters:
            self_conditions = cls.__build_conditions(self_filters)
            query = query.where(*self_conditions)
        return query

    @classmethod
    async def create(cls: Type["Base"], session: AsyncSession, commit: bool = True, **kwargs) -> "Base":
        obj = cls(**kwargs)
        session.add(obj)

        if commit:
            await session.commit()
            await session.refresh(obj)

        return obj

    @classmethod
    async def get(cls: Type["Base"], session: AsyncSession, **kwargs) -> List["Base"]:
        query = select(cls).filter_by(**kwargs) if kwargs else select(cls)
        result = await session.scalars(query)
        return result.all()

    @classmethod
    async def get_first(cls: Type["Base"], session: AsyncSession, **kwargs) -> Optional["Base"]:
        query = select(cls).filter_by(**kwargs)
        return await session.scalar(query)

    @classmethod
    async def update(
            cls: Type["Base"], session: AsyncSession, filters: Dict[str, Any], defaults: Dict[str, Any]
    ) -> int:
        if not defaults:
            return 0

        query = select(cls).filter_by(**filters)
        result = await session.scalars(query)
        objects = result.all()

        if not objects:
            return 0

        for obj in objects:
            for key, value in defaults.items():
                setattr(obj, key, value)
            session.add(obj)

        await session.commit()
        return len(objects)

    @classmethod
    async def delete(cls: Type["Base"], session: AsyncSession, **kwargs) -> int:
        query = select(cls).filter_by(**kwargs)
        result = await session.scalars(query)
        objs = result.all()
        if not objs:
            return 0
        for obj in objs:
            await session.delete(obj)
        await session.commit()
        return len(objs)

    @classmethod
    async def bulk_create(cls: Type["Base"], session: AsyncSession, data: list[Dict[str, Any]]) -> None:
        if not data:
            return
        query = insert(cls)
        await session.execute(query, data)
        await session.commit()

    @classmethod
    async def bulk_update(
            cls: Type["Base"], session: AsyncSession, filters: Dict[str, Any], defaults: Dict[str, Any]
    ) -> int:
        if not defaults:
            return 0
        query = update(cls).filter_by(**filters).values(**defaults)
        result = await session.execute(query)
        await session.commit()
        return result.rowcount

    @classmethod
    async def bulk_delete(cls: Type["Base"], session: AsyncSession, **kwargs) -> int:
        query = delete(cls).filter_by(**kwargs)
        result = await session.execute(query)
        await session.commit()
        return result.rowcount

    @classmethod
    async def get_or_create(
            cls: Type["Base"], session: AsyncSession, defaults: Dict[str, Any] = None, **kwargs
    ) -> Tuple["Base", bool]:
        defaults = defaults or {}
        obj = await cls.get_first(session=session, **kwargs)
        if obj:
            return obj, False

        obj = cls(**kwargs, **defaults)
        session.add(obj)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            obj = await session.scalar(select(cls).filter_by(**kwargs))
            return obj, False
        await session.refresh(obj)
        return obj, True

    @classmethod
    async def update_or_create(
            cls: Type["Base"], session: AsyncSession, defaults: Dict[str, Any] = None, **kwargs
    ) -> Tuple["Base", bool]:
        defaults = defaults or {}
        obj = await cls.get_first(session=session, **kwargs)
        if obj:
            for key, value in defaults.items():
                setattr(obj, key, value)
            session.add(obj)
            await session.commit()
            await session.refresh(obj)
            return obj, False

        obj = cls(**kwargs, **defaults)
        session.add(obj)
        await session.commit()
        await session.refresh(obj)
        return obj, True

    @classmethod
    async def find(
            cls: Type["Base"], session: AsyncSession, order_by: Union[str, List[str]] = None,
            limit: Optional[int] = None, or_filters: dict[str, Any] | None = None, **kwargs
    ) -> List["Base"]:
        query = cls.__build_query(filters=kwargs, or_filters=or_filters, order_by=order_by, limit=limit)
        result = await session.scalars(query)
        return result.all()

    @classmethod
    async def find_first(
            cls: Type["Base"], session: AsyncSession, or_filters: dict[str, Any] | None = None, **kwargs
    ) -> Optional["Base"]:
        query = cls.__build_query(filters=kwargs, or_filters=or_filters, limit=1)
        return await session.scalar(query)

    @classmethod
    async def update_by(
            cls: Type["Base"], session: AsyncSession, filters: dict[str, Any], defaults: dict[str, Any]
    ) -> int:
        if not defaults:
            return 0
        query = cls.__build_query(filters)
        result = await session.scalars(query)
        objs = result.all()

        if not objs:
            return 0

        for obj in objs:
            for key, value in defaults.items():
                setattr(obj, key, value)
            session.add(obj)

        await session.commit()
        return len(objs)

    @classmethod
    async def delete_by(cls: Type["Base"], session: AsyncSession, **filters) -> int:
        query = cls.__build_query(filters)
        result = await session.scalars(query)
        objs = result.all()
        if not objs:
            return 0

        for obj in objs:
            await session.delete(obj)

        await session.commit()
        return len(objs)

    @classmethod
    async def bulk_update_by(
            cls: Type["Base"], session: AsyncSession, filters: Dict[str, Any], defaults: Dict[str, Any]
    ) -> int:
        if not defaults:
            return 0
        query = update(cls).where(*cls.__build_conditions(filters)).values(**defaults)
        result = await session.execute(query)
        await session.commit()
        return result.rowcount

    @classmethod
    async def bulk_delete_by(cls: Type["Base"], session: AsyncSession, **filters) -> int:
        query = delete(cls).where(*cls.__build_conditions(filters))
        result = await session.execute(query)
        await session.commit()
        return result.rowcount

    @classmethod
    async def values_list(cls: Type["Base"], session: AsyncSession, fields: list[str], **filters) -> list:
        if not fields:
            raise ValueError("You must provide at least one field")

        conditions = cls.__build_conditions(filters)

        if len(fields) == 1:
            query = select(getattr(cls, fields[0])).where(*conditions)
            result = await session.scalars(query)
            return result.all()

        cols = [getattr(cls, f) for f in fields]
        query = select(*cols).where(*conditions)
        result = await session.execute(query)
        rows = result.fetchall()

        return [list(row) for row in rows]

    @classmethod
    async def exists(cls: Type["Base"], session: AsyncSession, **kwargs) -> bool:
        conditions = cls.__build_conditions(kwargs)
        # query = select(exists().where(*conditions))
        # return await session.scalar(query)
        query = select(cls).where(*conditions).limit(1)
        result = await session.scalar(query)
        return result is not None

    @classmethod
    async def find_join(
            cls: Type["Base"], related: Type["Base"], session: AsyncSession,
            self_filters: dict = None, related_filters: dict = None
    ) -> List["Base"]:
        self_filters = self_filters or {}
        related_filters = related_filters or {}

        self_conditions = cls.__build_conditions(self_filters)
        related_conditions = related.__build_conditions(related_filters)

        query = select(cls).join(related).where(*self_conditions, *related_conditions)
        result = await session.scalars(query)
        return result.all()



    @classmethod
    async def find_with_related(
            cls: Type["Base"], session: AsyncSession, related: Union[Type["Base"], List[Type["Base"]]],
            strategy: str = "select", self_filters: dict | None = None, related_filters: dict | None = None,
    ) -> List["Base"]:
        query = cls.__find_with_related(
            related=related,
            strategy=strategy,
            self_filters=self_filters,
            related_filters=related_filters
        )
        result = await session.scalars(query)
        return result.unique().all()

    @classmethod
    async def find_with_related_first(
            cls: Type["Base"], session: AsyncSession, related: Union[Type["Base"], List[Type["Base"]]],
            strategy: str = "select", self_filters: dict | None = None, related_filters: dict | None = None,
    ) -> Optional["Base"]:
        query = cls.__find_with_related(
            related=related,
            strategy=strategy,
            self_filters=self_filters,
            related_filters=related_filters
        )
        return await session.scalar(query)
