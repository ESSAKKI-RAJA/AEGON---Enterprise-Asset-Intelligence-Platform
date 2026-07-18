"""
AEGON Enterprise Repository Layer
Principal Architecture for Data Access Gateway

Python 3.12+ | SQLAlchemy 2.0 Async | Clean Architecture
"""

from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import (
    Any, Generic, Optional, TypeVar, Type, Dict, List
)
from uuid import UUID

from sqlalchemy import (
    or_, desc, asc, func, select, delete, 
    inspect
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError, NoResultFound
from sqlalchemy.sql import ColumnElement



# ============================================================================
# STRUCTURED LOGGING
# ============================================================================

class RepositoryLogger:
    """Enterprise-grade structured logging for repository operations."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
    
    def log_operation(
        self, 
        operation: str, 
        entity: str, 
        entity_id: Any, 
        status: str,
        duration_ms: float = 0,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log repository operation with structured context."""
        log_data = {
            "operation": operation,
            "entity": entity,
            "entity_id": str(entity_id),
            "status": status,
            "duration_ms": duration_ms,
            "timestamp": datetime.utcnow().isoformat(),
        }
        if metadata:
            log_data.update(metadata)
        
        self.logger.info(json.dumps(log_data))
    
    def log_error(
        self,
        operation: str,
        entity: str,
        error: Exception,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log repository errors with stack context."""
        log_data = {
            "operation": operation,
            "entity": entity,
            "error": str(error),
            "error_type": type(error).__name__,
            "timestamp": datetime.utcnow().isoformat(),
        }
        if metadata:
            log_data.update(metadata)
        
        self.logger.error(json.dumps(log_data), exc_info=True)


# ============================================================================
# REPOSITORY EXCEPTIONS - EXCEPTION TRANSLATION LAYER
# ============================================================================

class RepositoryException(Exception):
    """Base repository exception. Isolates database errors from application."""
    pass


class EntityNotFound(RepositoryException):
    """Entity does not exist."""
    pass


class EntityAlreadyExists(RepositoryException):
    """Entity violates unique constraint."""
    pass


class OptimisticLockError(RepositoryException):
    """Entity was modified by another transaction."""
    pass


class InvalidFilterSpecification(RepositoryException):
    """Filter specification is malformed."""
    pass


class TransactionError(RepositoryException):
    """Transaction failed."""
    pass


def translate_db_exception(exc: Exception) -> RepositoryException:
    """Translate SQLAlchemy exceptions to repository exceptions."""
    if isinstance(exc, RepositoryException):
        return exc
    if isinstance(exc, NoResultFound):
        return EntityNotFound("Entity not found")
    if isinstance(exc, IntegrityError):
        err_msg = str(exc).lower()
        if "unique" in err_msg:
            return EntityAlreadyExists("Entity violates unique constraint")
        if "check" in err_msg:
            return InvalidFilterSpecification("Entity violates check constraint")
        if "foreign key" in err_msg or "violates foreign key" in err_msg:
            return InvalidFilterSpecification("Entity violates foreign key constraint")
    if isinstance(exc, SQLAlchemyError):
        return RepositoryException(f"Database error: {str(exc)}")
    return RepositoryException(f"System error: {str(exc)}")


# ============================================================================
# FILTER SPECIFICATIONS - DYNAMIC FILTERING
# ============================================================================

class FilterOperator(str, Enum):
    """Filter operators for dynamic queries."""
    EQ = "eq"           # Equal
    NE = "ne"           # Not equal
    GT = "gt"           # Greater than
    GTE = "gte"         # Greater than or equal
    LT = "lt"           # Less than
    LTE = "lte"         # Less than or equal
    IN = "in"           # In list
    LIKE = "like"       # String contains
    ILIKE = "ilike"     # Case-insensitive contains
    IS_NULL = "is_null" # Is null
    BETWEEN = "between" # Range


@dataclass
class FilterSpec:
    """Single filter specification."""
    field: str
    operator: FilterOperator
    value: Any
    
    def to_sqlalchemy(self, model_cls: Type) -> ColumnElement:
        """Convert to SQLAlchemy filter expression."""
        if not hasattr(model_cls, self.field):
            raise InvalidFilterSpecification(f"Field '{self.field}' does not exist on model '{model_cls.__name__}'")
            
        column = getattr(model_cls, self.field)
        
        match self.operator:
            case FilterOperator.EQ:
                return column == self.value
            case FilterOperator.NE:
                return column != self.value
            case FilterOperator.GT:
                return column > self.value
            case FilterOperator.GTE:
                return column >= self.value
            case FilterOperator.LT:
                return column < self.value
            case FilterOperator.LTE:
                return column <= self.value
            case FilterOperator.IN:
                return column.in_(self.value)
            case FilterOperator.LIKE:
                return column.like(f"%{self.value}%")
            case FilterOperator.ILIKE:
                return column.ilike(f"%{self.value}%")
            case FilterOperator.IS_NULL:
                return column.is_(None) if self.value else column.is_not(None)
            case FilterOperator.BETWEEN:
                if not isinstance(self.value, (list, tuple)) or len(self.value) != 2:
                    raise InvalidFilterSpecification("BETWEEN requires [min, max]")
                return column.between(self.value[0], self.value[1])
            case _:
                raise InvalidFilterSpecification(f"Unknown operator: {self.operator}")


@dataclass
class QuerySpecification:
    """Query specification for flexible repository searches."""
    filters: List[FilterSpec] = field(default_factory=list)
    sort_by: Optional[str] = None
    sort_order: str = "asc"  # asc or desc
    page: int = 1
    page_size: int = 20
    search_query: Optional[str] = None
    search_fields: List[str] = field(default_factory=list)
    
    def apply_to_query(self, query, model_cls: Type):
        """Apply specification to SQLAlchemy query."""
        # Apply filters
        for filter_spec in self.filters:
            query = query.where(filter_spec.to_sqlalchemy(model_cls))
        
        # Apply full-text search
        if self.search_query and self.search_fields:
            search_conditions = []
            for field in self.search_fields:
                if hasattr(model_cls, field):
                    search_conditions.append(getattr(model_cls, field).ilike(f"%{self.search_query}%"))
            if search_conditions:
                query = query.where(or_(*search_conditions))
        
        # Apply sorting
        if self.sort_by and hasattr(model_cls, self.sort_by):
            column = getattr(model_cls, self.sort_by)
            if self.sort_order.lower() == "desc":
                query = query.order_by(desc(column))
            else:
                query = query.order_by(asc(column))
        
        return query


# ============================================================================
# PAGINATION
# ============================================================================

T = TypeVar('T')

@dataclass
class Page(Generic[T]):
    """Paginated result set."""
    items: List[T]
    total: int
    page: int
    page_size: int
    
    @property
    def total_pages(self) -> int:
        return (self.total + self.page_size - 1) // self.page_size if self.page_size > 0 else 0
    
    @property
    def has_next(self) -> bool:
        return self.page < self.total_pages
    
    @property
    def has_previous(self) -> bool:
        return self.page > 1


@dataclass
class CursorPage(Generic[T]):
    """Cursor-based pagination for large datasets."""
    items: List[T]
    cursor: Optional[str] = None
    has_more: bool = False


# ============================================================================
# REDIS CACHE HOOKS
# ============================================================================

class CacheHook(ABC):
    """Interface for repository cache integration."""
    
    @abstractmethod
    async def invalidate(self, entity_type: str, entity_id: Any):
        """Invalidate cache for entity."""
        pass
    
    @abstractmethod
    async def invalidate_pattern(self, pattern: str):
        """Invalidate cache matching pattern."""
        pass
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get from cache."""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int = 3600):
        """Set cache with TTL."""
        pass


class NoCacheHook(CacheHook):
    """No-op cache hook for testing."""
    
    async def invalidate(self, entity_type: str, entity_id: Any):
        pass
    
    async def invalidate_pattern(self, pattern: str):
        pass
    
    async def get(self, key: str) -> Optional[Any]:
        return None
    
    async def set(self, key: str, value: Any, ttl: int = 3600):
        pass


# ============================================================================
# AUDIT HOOKS
# ============================================================================

@dataclass
class AuditLog:
    """Audit trail for entity changes."""
    entity_type: str
    entity_id: UUID
    action: str  # create, update, delete, restore
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    changed_by: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


class AuditHook(ABC):
    """Interface for audit logging."""
    
    @abstractmethod
    async def log(self, audit: AuditLog):
        """Log audit event."""
        pass


class NoAuditHook(AuditHook):
    """No-op audit hook."""
    
    async def log(self, audit: AuditLog):
        pass


# ============================================================================
# OPTIMISTIC LOCKING
# ============================================================================

class OptimisticLock:
    """Optimistic locking support for concurrent updates."""
    
    @staticmethod
    def get_version(obj: Any) -> int:
        """Extract version from entity."""
        return getattr(obj, 'version', 0)
    
    @staticmethod
    def validate_version(obj: Any, current_version: int):
        """Validate object hasn't been modified."""
        if OptimisticLock.get_version(obj) != current_version:
            raise OptimisticLockError(
                f"Entity was modified by another transaction. "
                f"Expected version {current_version}, "
                f"got {OptimisticLock.get_version(obj)}"
            )


# ============================================================================
# BASE REPOSITORY - GENERIC CRUD + ENTERPRISE FEATURES
# ============================================================================

class BaseRepository(Generic[T], ABC):
    """
    Generic base repository implementing the Repository Pattern.
    """
    
    def __init__(
        self,
        session: AsyncSession,
        model_class: Type[T],
        cache_hook: Optional[CacheHook] = None,
        audit_hook: Optional[AuditHook] = None,
    ):
        self.session = session
        self.model_class = model_class
        self.cache_hook = cache_hook or NoCacheHook()
        self.audit_hook = audit_hook or NoAuditHook()
        self.logger = RepositoryLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
    
    # ========================================================================
    # BASIC CRUD
    # ========================================================================
    
    async def create(self, entity: T, audit_user: Optional[str] = None) -> T:
        """Create and persist entity."""
        try:
            self.session.add(entity)
            await self.session.flush()
            
            # Log audit
            if hasattr(entity, 'id'):
                await self.audit_hook.log(AuditLog(
                    entity_type=self.model_class.__name__,
                    entity_id=getattr(entity, 'id'),
                    action="create",
                    new_values=self._entity_to_dict(entity),
                    changed_by=audit_user,
                ))
                
                self.logger.log_operation(
                    "create",
                    self.model_class.__name__,
                    getattr(entity, 'id'),
                    "success"
                )
            
            return entity
        except Exception as e:
            await self.session.rollback()
            raise translate_db_exception(e)
    
    async def get_by_id(self, entity_id: Any) -> Optional[T]:
        """Retrieve entity by ID."""
        try:
            stmt = select(self.model_class).where(
                self.model_class.id == entity_id
            )
            # Filter soft deleted by default if model supports it
            if hasattr(self.model_class, 'is_deleted'):
                stmt = stmt.where(self.model_class.is_deleted .is_(False))
                
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            raise translate_db_exception(e)
    
    async def get_by_id_or_raise(self, entity_id: Any) -> T:
        """Retrieve entity by ID or raise."""
        entity = await self.get_by_id(entity_id)
        if not entity:
            raise EntityNotFound(f"Entity {entity_id} not found")
        return entity
    
    async def update(
        self, 
        entity: T, 
        audit_user: Optional[str] = None
    ) -> T:
        """Update entity with optimistic locking."""
        try:
            # Validate version if optimistic locking enabled
            if hasattr(entity, 'version'):
                current_version = getattr(entity, 'version')
                setattr(entity, 'version', current_version + 1)
            
            await self.session.flush()
            
            if hasattr(entity, 'id'):
                entity_id = getattr(entity, 'id')
                await self.audit_hook.log(AuditLog(
                    entity_type=self.model_class.__name__,
                    entity_id=entity_id,
                    action="update",
                    new_values=self._entity_to_dict(entity),
                    changed_by=audit_user,
                ))
                
                await self.cache_hook.invalidate(
                    self.model_class.__name__,
                    entity_id
                )
                
                self.logger.log_operation(
                    "update",
                    self.model_class.__name__,
                    entity_id,
                    "success"
                )
            
            return entity
        except Exception as e:
            await self.session.rollback()
            raise translate_db_exception(e)
    
    async def delete(self, entity_id: Any, audit_user: Optional[str] = None) -> bool:
        """Delete entity (hard delete)."""
        try:
            entity = await self.get_by_id_or_raise(entity_id)
            await self.session.delete(entity)
            await self.session.flush()
            
            await self.audit_hook.log(AuditLog(
                entity_type=self.model_class.__name__,
                entity_id=entity_id,
                action="delete",
                old_values=self._entity_to_dict(entity),
                changed_by=audit_user,
            ))
            
            await self.cache_hook.invalidate(self.model_class.__name__, entity_id)
            
            self.logger.log_operation(
                "delete",
                self.model_class.__name__,
                entity_id,
                "success"
            )
            
            return True
        except Exception as e:
            await self.session.rollback()
            raise translate_db_exception(e)
    
    # ========================================================================
    # SOFT DELETE & RESTORE
    # ========================================================================
    
    async def soft_delete(
        self, 
        entity_id: Any, 
        audit_user: Optional[str] = None
    ) -> T:
        """Soft delete entity (mark as deleted)."""
        try:
            entity = await self.get_by_id_or_raise(entity_id)
            if hasattr(entity, 'is_deleted'):
                setattr(entity, 'is_deleted', True)
            if hasattr(entity, 'deleted_at'):
                setattr(entity, 'deleted_at', datetime.utcnow())
            if hasattr(entity, 'deleted_by'):
                setattr(entity, 'deleted_by', audit_user)
            
            await self.session.flush()
            
            await self.audit_hook.log(AuditLog(
                entity_type=self.model_class.__name__,
                entity_id=entity_id,
                action="delete",
                changed_by=audit_user,
            ))
            
            await self.cache_hook.invalidate(self.model_class.__name__, entity_id)
            
            return entity
        except Exception as e:
            await self.session.rollback()
            raise translate_db_exception(e)
    
    async def restore(
        self, 
        entity_id: Any, 
        audit_user: Optional[str] = None
    ) -> T:
        """Restore soft-deleted entity."""
        try:
            entity = await self.get_by_id_or_raise(entity_id)
            if hasattr(entity, 'is_deleted'):
                setattr(entity, 'is_deleted', False)
            if hasattr(entity, 'deleted_at'):
                setattr(entity, 'deleted_at', None)
            if hasattr(entity, 'deleted_by'):
                setattr(entity, 'deleted_by', None)
            
            await self.session.flush()
            
            await self.audit_hook.log(AuditLog(
                entity_type=self.model_class.__name__,
                entity_id=entity_id,
                action="restore",
                changed_by=audit_user,
            ))
            
            await self.cache_hook.invalidate(self.model_class.__name__, entity_id)
            
            return entity
        except Exception as e:
            await self.session.rollback()
            raise translate_db_exception(e)
    
    # ========================================================================
    # BULK OPERATIONS
    # ========================================================================
    
    async def create_bulk(
        self, 
        entities: List[T],
        audit_user: Optional[str] = None
    ) -> List[T]:
        """Create multiple entities in single batch."""
        try:
            self.session.add_all(entities)
            await self.session.flush()
            
            for entity in entities:
                if hasattr(entity, 'id'):
                    await self.audit_hook.log(AuditLog(
                        entity_type=self.model_class.__name__,
                        entity_id=getattr(entity, 'id'),
                        action="create",
                        new_values=self._entity_to_dict(entity),
                        changed_by=audit_user,
                    ))
            
            self.logger.log_operation(
                "create_bulk",
                self.model_class.__name__,
                len(entities),
                "success",
                metadata={"count": len(entities)}
            )
            
            return entities
        except Exception as e:
            await self.session.rollback()
            raise translate_db_exception(e)
    
    async def update_bulk(
        self,
        updates: Dict[Any, Dict[str, Any]],
        audit_user: Optional[str] = None
    ) -> List[T]:
        """Update multiple entities by ID."""
        try:
            updated = []
            for entity_id, values in updates.items():
                entity = await self.get_by_id_or_raise(entity_id)
                for key, value in values.items():
                    setattr(entity, key, value)
                updated.append(entity)
            
            await self.session.flush()
            
            for entity in updated:
                if hasattr(entity, 'id'):
                    await self.cache_hook.invalidate(
                        self.model_class.__name__,
                        getattr(entity, 'id')
                    )
            
            return updated
        except Exception as e:
            await self.session.rollback()
            raise translate_db_exception(e)
    
    async def delete_bulk(
        self,
        entity_ids: List[Any],
        audit_user: Optional[str] = None
    ) -> int:
        """Delete multiple entities."""
        try:
            stmt = delete(self.model_class).where(
                self.model_class.id.in_(entity_ids)
            )
            result = await self.session.execute(stmt)
            await self.session.flush()
            
            for entity_id in entity_ids:
                await self.cache_hook.invalidate(
                    self.model_class.__name__,
                    entity_id
                )
            
            return result.rowcount
        except Exception as e:
            await self.session.rollback()
            raise translate_db_exception(e)
    
    # ========================================================================
    # QUERYING & FILTERING
    # ========================================================================
    
    async def find_by_spec(
        self, 
        spec: QuerySpecification
    ) -> Page[T]:
        """Find entities matching specification."""
        try:
            # Build base query
            query = select(self.model_class)
            
            # Exclude soft-deleted by default
            if hasattr(self.model_class, 'is_deleted'):
                query = query.where(self.model_class.is_deleted .is_(False))
            
            # Apply specification
            query = spec.apply_to_query(query, self.model_class)
            
            # Count total (without limit/offset)
            count_query = select(func.count()).select_from(self.model_class)
            if hasattr(self.model_class, 'is_deleted'):
                count_query = count_query.where(self.model_class.is_deleted .is_(False))
            for filter_spec in spec.filters:
                count_query = count_query.where(filter_spec.to_sqlalchemy(self.model_class))
            if spec.search_query and spec.search_fields:
                search_conditions = []
                for field in spec.search_fields:
                    if hasattr(self.model_class, field):
                        search_conditions.append(getattr(self.model_class, field).ilike(f"%{spec.search_query}%"))
                if search_conditions:
                    count_query = count_query.where(or_(*search_conditions))
                    
            count_result = await self.session.execute(count_query)
            total = count_result.scalar() or 0
            
            # Apply pagination
            offset = (spec.page - 1) * spec.page_size
            query = query.offset(offset).limit(spec.page_size)
            
            # Execute
            result = await self.session.execute(query)
            items = result.scalars().all()
            
            return Page(
                items=list(items),
                total=total,
                page=spec.page,
                page_size=spec.page_size
            )
        except Exception as e:
            raise translate_db_exception(e)
    
    async def find_by_filter(
        self,
        filters: List[FilterSpec],
        page: int = 1,
        page_size: int = 20
    ) -> Page[T]:
        """Find with simple filters and pagination."""
        spec = QuerySpecification(
            filters=filters,
            page=page,
            page_size=page_size
        )
        return await self.find_by_spec(spec)
    
    async def search(
        self,
        query: str,
        search_fields: List[str],
        page: int = 1,
        page_size: int = 20
    ) -> Page[T]:
        """Full-text search across fields."""
        spec = QuerySpecification(
            search_query=query,
            search_fields=search_fields,
            page=page,
            page_size=page_size
        )
        return await self.find_by_spec(spec)
    
    async def get_all(
        self,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
        page: int = 1,
        page_size: int = 20
    ) -> Page[T]:
        """Get all entities with pagination."""
        spec = QuerySpecification(
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            page_size=page_size
        )
        return await self.find_by_spec(spec)
    
    # ========================================================================
    # UTILITIES
    # ========================================================================
    
    def _entity_to_dict(self, entity: T) -> Dict[str, Any]:
        """Convert entity to dict for logging."""
        mapper = inspect(self.model_class)
        return {
            col.name: getattr(entity, col.name)
            for col in mapper.columns
        }


# ============================================================================
# UNIT OF WORK PATTERN
# ============================================================================

class UnitOfWork:
    """
    Unit of Work pattern for coordinating multiple repositories
    and managing transactions.
    """
    
    def __init__(self, session: AsyncSession, cache_hook: Optional['CacheHook'] = None, audit_hook: Optional['AuditHook'] = None):
        self.session = session
        self.cache_hook = cache_hook
        self.audit_hook = audit_hook
        self._repositories: Dict[Type, BaseRepository] = {}
    
    def register_repository(self, repo_class: Type[BaseRepository], repo: BaseRepository):
        """Register a repository."""
        self._repositories[repo_class] = repo
    
    def get_repository(self, repo_class: Type[BaseRepository]) -> BaseRepository:
        """Get registered repository or instantiate it lazily."""
        if repo_class not in self._repositories:
            self._repositories[repo_class] = repo_class(
                session=self.session,
                cache_hook=self.cache_hook,
                audit_hook=self.audit_hook
            )
        return self._repositories[repo_class]
    
    async def commit(self):
        """Commit transaction."""
        try:
            await self.session.commit()
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise TransactionError(f"Commit failed: {str(e)}")
    
    async def rollback(self):
        """Rollback transaction."""
        await self.session.rollback()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
        else:
            await self.commit()
