"""
Generic Base Repository.

Provides the reusable CRUD abstraction documented as the common shape
of every repository interface (ILearnerRepository, IAssessmentRepository,
ICourseRepository, ITopicRepository): save/create, findById, findAll,
update, delete — plus pagination, filtering, and sorting.

Reference: 03_SOFTWARE_DESIGN/03_Interface_Design.md (Section 6 - Repository Interfaces)
Reference: 03_SOFTWARE_DESIGN/02_Class_Design.md (Section 12 - Repository Classes)
Reference: 03_SOFTWARE_DESIGN/01_Package_Design.md (Section 5.5 - Repository Package)

Transaction boundaries: repository methods `flush()` (making changes
visible within the current transaction and assigning generated keys)
but never `commit()`. Committing — and therefore the transaction
boundary — is the caller's responsibility. This keeps repositories
composable within a larger unit of work managed by the service layer
(Module 5+), consistent with `core/dependencies.get_db()` only
`close()`-ing the session rather than committing it.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from sqlalchemy import Select, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import InstrumentedAttribute, Session
from sqlalchemy.orm.interfaces import LoaderOption

from backend.core.exceptions import ConflictError, NotFoundError
from backend.core.logging import get_logger
from backend.database.base import Base

ModelType = TypeVar("ModelType", bound=Base)

logger = get_logger(__name__)


@dataclass(frozen=True)
class Page(Generic[ModelType]):
    """A single page of results, plus the total row count matching the filters."""

    items: list[ModelType]
    total: int
    offset: int
    limit: int


class BaseRepository(Generic[ModelType]):
    """
    Generic repository providing CRUD, pagination, filtering, and
    sorting for a single SQLAlchemy model.

    Subclasses set `model` to their entity class and may override
    `default_load_options` to eager-load relationships commonly needed
    alongside that entity, avoiding N+1 queries.
    """

    model: type[ModelType]
    default_load_options: tuple[LoaderOption, ...] = ()

    def __init__(self, db: Session) -> None:
        self.db = db

    # ------------------------------------------------------------------
    # Create / Save
    # ------------------------------------------------------------------
    def create(self, **fields: Any) -> ModelType:
        """Creates and persists a new entity from the given fields."""
        obj = self.model(**fields)
        self.db.add(obj)
        self._flush()
        self.db.refresh(obj)
        logger.info("Created %s", _describe(obj))
        return obj

    def save(self, obj: ModelType) -> ModelType:
        """Persists an already-constructed entity instance (documented as `save()`)."""
        self.db.add(obj)
        self._flush()
        self.db.refresh(obj)
        logger.info("Saved %s", _describe(obj))
        return obj

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------
    def find_by_id(self, id_: Any) -> ModelType | None:
        """Returns the entity with the given primary key, or None."""
        stmt: Select[Any] = select(self.model)
        for option in self.default_load_options:
            stmt = stmt.options(option)
        stmt = stmt.where(self._pk_column() == id_)
        return self.db.execute(stmt).unique().scalar_one_or_none()

    def find_all(
        self,
        *,
        offset: int = 0,
        limit: int = 50,
        order_by: InstrumentedAttribute[Any] | None = None,
        descending: bool = False,
        **equality_filters: Any,
    ) -> Page[ModelType]:
        """
        Returns a page of entities matching the given equality filters
        (column_name=value), sorted by `order_by` if given.
        """
        stmt: Select[Any] = select(self.model)
        stmt = self._apply_filters(stmt, equality_filters)
        for option in self.default_load_options:
            stmt = stmt.options(option)

        count_stmt = self._apply_filters(select(func.count()).select_from(self.model), equality_filters)
        total = self.db.execute(count_stmt).scalar_one()

        if order_by is not None:
            stmt = stmt.order_by(order_by.desc() if descending else order_by.asc())
        stmt = stmt.offset(offset).limit(limit)

        items = list(self.db.execute(stmt).unique().scalars().all())
        return Page(items=items, total=total, offset=offset, limit=limit)

    def count(self, **equality_filters: Any) -> int:
        """Returns the number of entities matching the given equality filters."""
        stmt = self._apply_filters(select(func.count()).select_from(self.model), equality_filters)
        return self.db.execute(stmt).scalar_one()

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------
    def update(self, id_: Any, **fields: Any) -> ModelType:
        """Updates the entity with the given primary key. Raises NotFoundError if missing."""
        obj = self.find_by_id(id_)
        if obj is None:
            raise NotFoundError(f"{self.model.__name__} with id={id_!r} was not found.")
        for field_name, value in fields.items():
            setattr(obj, field_name, value)
        self._flush()
        self.db.refresh(obj)
        logger.info("Updated %s", _describe(obj))
        return obj

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------
    def delete(self, id_: Any) -> None:
        """Deletes the entity with the given primary key. Raises NotFoundError if missing."""
        obj = self.find_by_id(id_)
        if obj is None:
            raise NotFoundError(f"{self.model.__name__} with id={id_!r} was not found.")
        self.db.delete(obj)
        self._flush()
        logger.info("Deleted %s(id=%r)", self.model.__name__, id_)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    def _pk_column(self) -> InstrumentedAttribute[Any]:
        pk_columns = list(self.model.__mapper__.primary_key)
        return getattr(self.model, pk_columns[0].name)

    def _apply_filters(self, stmt: Select[Any], filters: dict[str, Any]) -> Select[Any]:
        for field_name, value in filters.items():
            if not hasattr(self.model, field_name):
                raise ValueError(f"{self.model.__name__} has no filterable field {field_name!r}.")
            stmt = stmt.where(getattr(self.model, field_name) == value)
        return stmt

    def _flush(self) -> None:
        try:
            self.db.flush()
        except IntegrityError as exc:
            self.db.rollback()
            logger.warning("Integrity error persisting %s: %s", self.model.__name__, exc)
            raise ConflictError(
                f"A database constraint was violated while saving {self.model.__name__}."
            ) from exc


def _describe(obj: Base) -> str:
    return repr(obj)