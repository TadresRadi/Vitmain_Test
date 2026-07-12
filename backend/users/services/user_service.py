"""
User service for handling user-related business logic.
"""
import logging
from typing import Optional, Dict, Any
from django.contrib.auth import get_user_model
from django.utils import timezone
from core.services import BaseService, ServiceException
from core.utils import log_user_activity

User = get_user_model()
logger = logging.getLogger(__name__)


class UserService(BaseService[User]):
    """Service for user operations."""
    model_class = User
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            logger.debug(f"User not found with email: {email}")
            return None
        except Exception as e:
            logger.error(f"Error getting user by email: {str(e)}")
            return None
    
    def user_exists(self, email: str) -> bool:
        """Check if user exists by email."""
        return self.exists(email=email)
    
    def create_user(
        self,
        email: str,
        password: Optional[str] = None,
        **kwargs
    ) -> Optional[User]:
        """
        Create a new user.
        
        Args:
            email: User email
            password: Optional password
            **kwargs: Additional user fields
        
        Returns:
            Created user or None on error
        """
        if self.user_exists(email):
            logger.warning(f"User already exists: {email}")
            raise ServiceException(f"User with email {email} already exists")
        
        try:
            user = User.objects.create_user(email=email, password=password, **kwargs)
            log_user_activity(user, 'user_created', {'email': email})
            logger.info(f"Created user: {email}")
            return user
        except Exception as e:
            logger.error(f"Error creating user {email}: {str(e)}")
            raise ServiceException(f"Failed to create user: {str(e)}")
    
    def update_user(
        self,
        user_id: Any,
        **kwargs
    ) -> Optional[User]:
        """
        Update user fields.
        
        Args:
            user_id: User ID
            **kwargs: Fields to update
        
        Returns:
            Updated user or None
        """
        try:
            user = self.get_by_id(user_id)
            if not user:
                raise ServiceException(f"User not found: {user_id}")
            
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            
            user.save()
            log_user_activity(user, 'user_updated', kwargs)
            logger.info(f"Updated user: {user.email}")
            return user
        except ServiceException:
            raise
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {str(e)}")
            raise ServiceException(f"Failed to update user: {str(e)}")
    
    def update_last_login(self, user_id: Any) -> bool:
        """Update user's last login timestamp."""
        try:
            user = self.get_by_id(user_id)
            if user:
                user.last_login = timezone.now()
                user.save(update_fields=['last_login'])
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating last login: {str(e)}")
            return False
    
    def get_user_stats(self, user_id: Any) -> Optional[Dict[str, Any]]:
        """Get user statistics."""
        try:
            user = self.get_by_id(user_id)
            if not user:
                return None
            
            return {
                'id': str(user.id),
                'email': user.email,
                'full_name': user.full_name,
                'role': user.role,
                'user_type': user.user_type,
                'auth_provider': user.auth_provider,
                'onboarding_completed': user.onboarding_completed,
                'posts_generated': user.posts_generated,
                'images_generated': user.images_generated,
                'date_joined': user.date_joined.isoformat(),
                'last_login': user.last_login.isoformat() if user.last_login else None,
            }
        except Exception as e:
            logger.error(f"Error getting user stats: {str(e)}")
            return None
    
    def deactivate_user(self, user_id: Any) -> bool:
        """Deactivate a user account."""
        try:
            user = self.update(user_id, is_active=False)
            if user:
                log_user_activity(user, 'user_deactivated', {})
                return True
            return False
        except Exception as e:
            logger.error(f"Error deactivating user: {str(e)}")
            return False


# Singleton instance
_user_service = None


def get_user_service() -> UserService:
    """Get or create user service singleton."""
    global _user_service
    if _user_service is None:
        _user_service = UserService()
    return _user_service