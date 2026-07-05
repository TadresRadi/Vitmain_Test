"""
Repository pattern for database access abstraction.
"""
import logging
from typing import Any, Dict, Optional, List
from django.db import models
from django.db.models.query import QuerySet

logger = logging.getLogger(__name__)


class BaseRepository:
    """Base repository for database operations."""
    
    def __init__(self, model_class: type):
        self.model_class = model_class
    
    def get(self, **kwargs) -> Optional[models.Model]:
        """Get single object or None."""
        try:
            return self.model_class.objects.get(**kwargs)
        except self.model_class.DoesNotExist:
            return None
        except Exception as e:
            logger.error(f"Error fetching {self.model_class.__name__}: {str(e)}")
            return None
    
    def filter(self, **kwargs) -> QuerySet:
        """Filter objects."""
        return self.model_class.objects.filter(**kwargs)
    
    def all(self) -> QuerySet:
        """Get all objects."""
        return self.model_class.objects.all()
    
    def create(self, **kwargs) -> Optional[models.Model]:
        """Create object."""
        try:
            return self.model_class.objects.create(**kwargs)
        except Exception as e:
            logger.error(f"Error creating {self.model_class.__name__}: {str(e)}")
            return None
    
    def update(self, obj: models.Model, **kwargs) -> Optional[models.Model]:
        """Update object."""
        try:
            for key, value in kwargs.items():
                setattr(obj, key, value)
            obj.save()
            return obj
        except Exception as e:
            logger.error(f"Error updating {self.model_class.__name__}: {str(e)}")
            return None
    
    def delete(self, **kwargs) -> bool:
        """Delete objects."""
        try:
            return self.model_class.objects.filter(**kwargs).delete()[0] > 0
        except Exception as e:
            logger.error(f"Error deleting {self.model_class.__name__}: {str(e)}")
            return False


class UserRepository(BaseRepository):
    """Repository for User model operations."""
    
    def get_by_email(self, email: str) -> Optional[models.Model]:
        """Get user by email."""
        return self.get(email=email)
    
    def email_exists(self, email: str) -> bool:
        """Check if email exists."""
        return self.model_class.objects.filter(email=email).exists()
    
    def get_active_users(self) -> QuerySet:
        """Get all active users."""
        return self.filter(is_active=True)
    
    def get_users_by_role(self, role: str) -> QuerySet:
        """Get users by role."""
        return self.filter(role=role)