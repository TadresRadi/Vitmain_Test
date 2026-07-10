"""
Base service classes for business logic abstraction.
"""
import logging
from typing import Any, Optional, TypeVar, Generic
from django.db import models
from django.db.models.query import QuerySet
from rest_framework import status

from core.exceptions import VitmainAPIException

logger = logging.getLogger(__name__)
T = TypeVar('T', bound=models.Model)


class BaseService(Generic[T]):
    """
    Base service class providing common CRUD operations.
    Subclasses should define model_class attribute.

    Design principle: DoesNotExist is a legitimate "not found" result
    and returns None. All other exceptions propagate to the caller so
    they can be handled by the global exception handler or caught
    explicitly by the view layer.
    """

    model_class: type[T] = None

    def __init__(self):
        if self.model_class is None:
            raise ValueError(f"{self.__class__.__name__} must define model_class")

    def get_by_id(self, obj_id: Any) -> Optional[T]:
        """
        Get object by primary key.

        Returns None if the object does not exist.
        Any other database errors propagate to the caller.
        """
        try:
            return self.model_class.objects.get(pk=obj_id)
        except self.model_class.DoesNotExist:
            logger.debug(f"{self.model_class.__name__} not found: {obj_id}")
            return None

    def get_all(self) -> QuerySet:
        """Get all objects."""
        return self.model_class.objects.all()

    def filter(self, **kwargs) -> QuerySet:
        """Filter objects by kwargs."""
        return self.model_class.objects.filter(**kwargs)

    def create(self, **kwargs) -> T:
        """
        Create new object.

        Returns the created object.
        Raises the underlying database exception on failure (e.g.,
        IntegrityError for constraint violations). Callers should
        handle exceptions as appropriate for their use case.
        """
        obj = self.model_class.objects.create(**kwargs)
        logger.info(f"Created {self.model_class.__name__}: {obj}")
        return obj

    def update(self, obj_id: Any, **kwargs) -> Optional[T]:
        """
        Update object fields.

        Returns None if the object does not exist.
        Raises the underlying database exception on save failure.
        """
        obj = self.get_by_id(obj_id)
        if not obj:
            return None

        for key, value in kwargs.items():
            setattr(obj, key, value)
        obj.save()
        logger.info(f"Updated {self.model_class.__name__}: {obj}")
        return obj

    def delete(self, obj_id: Any) -> bool:
        """
        Delete object.

        Returns False if the object does not exist.
        Raises the underlying database exception on delete failure.
        """
        obj = self.get_by_id(obj_id)
        if not obj:
            return False

        obj.delete()
        logger.info(f"Deleted {self.model_class.__name__}: {obj_id}")
        return True

    def exists(self, **kwargs) -> bool:
        """Check if object exists."""
        return self.model_class.objects.filter(**kwargs).exists()

    def count(self, **kwargs) -> int:
        """Count objects."""
        return self.model_class.objects.filter(**kwargs).count()


class ServiceException(VitmainAPIException):
    """
    Exception for service layer errors.

    Subclasses VitmainAPIException so that the global exception handler
    (core.exception_handlers) can format it consistently when it
    propagates out of a view without being explicitly caught.

    Default status is 500. For specific HTTP statuses, views should
    catch ServiceException and re-raise as a more specific
    VitmainAPIException subclass (e.g. ExternalServiceError for 503,
    ConflictError for 409, NotFoundError for 404).
    """
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "Service error"
    default_code = "service_error"