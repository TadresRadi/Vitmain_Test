"""
Base service classes for business logic abstraction.
"""
import logging
from typing import Any, Dict, Optional, List, TypeVar, Generic
from django.db import models
from django.db.models.query import QuerySet

logger = logging.getLogger(__name__)
T = TypeVar('T', bound=models.Model)


class BaseService(Generic[T]):
    """
    Base service class providing common CRUD operations.
    Subclasses should define model_class attribute.
    """
    model_class: type[T] = None
    
    def __init__(self):
        if self.model_class is None:
            raise ValueError(f"{self.__class__.__name__} must define model_class")
    
    def get_by_id(self, obj_id: Any) -> Optional[T]:
        """Get object by primary key."""
        try:
            return self.model_class.objects.get(pk=obj_id)
        except self.model_class.DoesNotExist:
            logger.warning(f"{self.model_class.__name__} not found: {obj_id}")
            return None
        except Exception as e:
            logger.error(f"Error getting {self.model_class.__name__}: {str(e)}")
            return None
    
    def get_all(self) -> QuerySet:
        """Get all objects."""
        return self.model_class.objects.all()
    
    def filter(self, **kwargs) -> QuerySet:
        """Filter objects by kwargs."""
        return self.model_class.objects.filter(**kwargs)
    
    def create(self, **kwargs) -> Optional[T]:
        """Create new object."""
        try:
            obj = self.model_class.objects.create(**kwargs)
            logger.info(f"Created {self.model_class.__name__}: {obj}")
            return obj
        except Exception as e:
            logger.error(f"Error creating {self.model_class.__name__}: {str(e)}")
            return None
    
    def update(self, obj_id: Any, **kwargs) -> Optional[T]:
        """Update object."""
        try:
            obj = self.get_by_id(obj_id)
            if not obj:
                return None
            
            for key, value in kwargs.items():
                setattr(obj, key, value)
            obj.save()
            logger.info(f"Updated {self.model_class.__name__}: {obj}")
            return obj
        except Exception as e:
            logger.error(f"Error updating {self.model_class.__name__}: {str(e)}")
            return None
    
    def delete(self, obj_id: Any) -> bool:
        """Delete object."""
        try:
            obj = self.get_by_id(obj_id)
            if obj:
                obj.delete()
                logger.info(f"Deleted {self.model_class.__name__}: {obj_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting {self.model_class.__name__}: {str(e)}")
            return False
    
    def exists(self, **kwargs) -> bool:
        """Check if object exists."""
        return self.model_class.objects.filter(**kwargs).exists()
    
    def count(self, **kwargs) -> int:
        """Count objects."""
        return self.model_class.objects.filter(**kwargs).count()


class ServiceException(Exception):
    """Custom exception for service layer."""
    pass