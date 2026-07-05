"""
API Key management service.
Handles generation, validation, rotation, and revocation.
"""
import logging
import secrets
import hashlib
from typing import Optional, Tuple, Dict, Any
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.utils import timezone
from core.api_key_models import APIKey, APIKeyAuditLog

User = get_user_model()
logger = logging.getLogger(__name__)

# API Key format: vitmain_<timestamp>_<random>
API_KEY_PREFIX = 'vitmain_'
API_KEY_LENGTH = 48  # Total length minus prefix


class APIKeyService:
    """Service for managing API keys."""

    @staticmethod
    def generate_key() -> str:
        """
        Generate a new API key.
        
        Returns:
            Generated API key string
        """
        # Generate random bytes
        random_part = secrets.token_urlsafe(API_KEY_LENGTH)
        
        # Create full key
        key = f"{API_KEY_PREFIX}{random_part}"
        
        logger.debug(f"Generated new API key: {key[:20]}...")
        return key

    @staticmethod
    def hash_key(key: str) -> str:
        """
        Hash API key for storage.
        Never store raw keys in database.
        
        Args:
            key: Raw API key
        
        Returns:
            SHA256 hash of key
        """
        return hashlib.sha256(key.encode()).hexdigest()

    @staticmethod
    def get_key_prefix(key: str) -> str:
        """
        Get prefix (first 32 chars) of API key.
        Used for identifying key without exposing full key.
        
        Args:
            key: Raw API key
        
        Returns:
            Key prefix
        """
        return key[:32]

    @staticmethod
    def create_api_key(
        user: User,
        name: str,
        scope: str = 'read',
        expires_in_days: Optional[int] = None,
        description: str = '',
        allowed_ips: list = None,
    ) -> Tuple[str, APIKey]:
        """
        Create a new API key for user.
        
        Args:
            user: User instance
            name: Friendly name
            scope: Access scope (read, write, admin)
            expires_in_days: Days until expiry (None = never)
            description: Description
            allowed_ips: List of allowed IPs
        
        Returns:
            Tuple of (raw_key, APIKey_instance)
        
        Raises:
            ValueError: If validation fails
        """
        try:
            # Validate scope
            valid_scopes = [s[0] for s in APIKey.SCOPE_CHOICES]
            if scope not in valid_scopes:
                raise ValueError(f"Invalid scope: {scope}")
            
            # Validate name
            if not name or len(name) < 3:
                raise ValueError("Name must be at least 3 characters")
            
            # Check if name already exists for user
            if APIKey.objects.filter(user=user, name=name).exists():
                raise ValueError(f"Key name '{name}' already exists for this user")
            
            # Generate key
            raw_key = APIKeyService.generate_key()
            key_prefix = APIKeyService.get_key_prefix(raw_key)
            key_hash = APIKeyService.hash_key(raw_key)
            
            # Calculate expiry
            expires_at = None
            if expires_in_days:
                expires_at = timezone.now() + timedelta(days=expires_in_days)
            
            # Create API key record
            api_key = APIKey.objects.create(
                user=user,
                name=name,
                key_prefix=key_prefix,
                key_hash=key_hash,
                scope=scope,
                expires_at=expires_at,
                description=description,
                allowed_ips=allowed_ips or [],
            )
            
            # Log creation
            APIKeyAuditLog.log_event(
                api_key=api_key,
                event_type='created',
                user=user,
                description=f"Created new API key: {name}",
                metadata={
                    'scope': scope,
                    'expires_in_days': expires_in_days,
                }
            )
            
            logger.info(f"Created API key for user: {user.email}")
            return raw_key, api_key
        
        except ValueError as e:
            logger.warning(f"Error creating API key: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error creating API key: {str(e)}")
            raise

    @staticmethod
    def validate_key(key: str) -> Optional[APIKey]:
        """
        Validate API key and return associated APIKey instance.
        
        Args:
            key: Raw API key
        
        Returns:
            APIKey instance if valid, None otherwise
        """
        try:
            if not key or not key.startswith(API_KEY_PREFIX):
                logger.warning("Invalid API key format")
                return None
            
            # Hash the key
            key_hash = APIKeyService.hash_key(key)
            
            # Look up in database
            try:
                api_key = APIKey.objects.get(key_hash=key_hash)
            except APIKey.DoesNotExist:
                logger.warning("API key not found")
                return None
            
            # Check if valid
            if not api_key.is_valid():
                logger.warning(f"API key is not valid: {api_key.status}")
                return None
            
            return api_key
        
        except Exception as e:
            logger.error(f"Error validating API key: {str(e)}")
            return None

    @staticmethod
    def authenticate_with_key(
        key: str,
        ip_address: str = None,
    ) -> Optional[APIKey]:
        """
        Authenticate request using API key.
        Checks validity, IP restrictions, and logs usage.
        
        Args:
            key: Raw API key
            ip_address: Client IP address
        
        Returns:
            APIKey instance if valid, None otherwise
        """
        try:
            # Validate key
            api_key = APIKeyService.validate_key(key)
            if not api_key:
                return None
            
            # Check IP restriction
            if ip_address and not api_key.is_ip_allowed(ip_address):
                logger.warning(f"IP not allowed for key: {ip_address}")
                
                APIKeyAuditLog.log_event(
                    api_key=api_key,
                    event_type='ip_blocked',
                    ip_address=ip_address,
                    description=f"Access blocked from unauthorized IP"
                )
                
                return None
            
            # Update last used
            api_key.update_last_used(ip_address)
            
            # Log usage
            APIKeyAuditLog.log_event(
                api_key=api_key,
                event_type='used',
                ip_address=ip_address,
                description=f"API key used"
            )
            
            return api_key
        
        except Exception as e:
            logger.error(f"Error authenticating with API key: {str(e)}")
            return None

    @staticmethod
    def rotate_key(api_key: APIKey, user: User) -> Tuple[str, APIKey]:
        """
        Rotate an API key (create new, mark old as rotated).
        
        Args:
            api_key: APIKey to rotate
            user: User performing rotation
        
        Returns:
            Tuple of (new_raw_key, new_APIKey_instance)
        
        Raises:
            ValueError: If cannot rotate
        """
        try:
            if api_key.user != user:
                raise ValueError("User cannot rotate another user's key")
            
            if api_key.status != 'active':
                raise ValueError("Cannot rotate inactive key")
            
            # Create new key with same settings
            new_raw_key, new_api_key = APIKeyService.create_api_key(
                user=user,
                name=f"{api_key.name} (rotated)",
                scope=api_key.scope,
                expires_in_days=(
                    (api_key.expires_at - timezone.now()).days
                    if api_key.expires_at else None
                ),
                description=api_key.description,
                allowed_ips=api_key.allowed_ips,
            )
            
            # Mark old key as rotated
            api_key.status = 'inactive'
            api_key.rotated_at = timezone.now()
            api_key.save()
            
            # Log rotation
            APIKeyAuditLog.log_event(
                api_key=api_key,
                event_type='rotated',
                user=user,
                description=f"Key rotated to: {new_api_key.key_prefix}"
            )
            
            logger.info(f"Rotated API key for user: {user.email}")
            return new_raw_key, new_api_key
        
        except ValueError as e:
            logger.warning(f"Error rotating key: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error rotating API key: {str(e)}")
            raise

    @staticmethod
    def revoke_key(api_key: APIKey, user: User, reason: str = '') -> bool:
        """
        Revoke an API key.
        
        Args:
            api_key: APIKey to revoke
            user: User revoking the key
            reason: Reason for revocation
        
        Returns:
            True if revoked successfully
        
        Raises:
            ValueError: If cannot revoke
        """
        try:
            if api_key.user != user:
                raise ValueError("User cannot revoke another user's key")
            
            if api_key.status == 'revoked':
                raise ValueError("Key already revoked")
            
            # Revoke key
            api_key.status = 'revoked'
            api_key.save()
            
            # Log revocation
            APIKeyAuditLog.log_event(
                api_key=api_key,
                event_type='revoked',
                user=user,
                description=f"Key revoked: {reason}"
            )
            
            logger.info(f"Revoked API key for user: {user.email}")
            return True
        
        except ValueError as e:
            logger.warning(f"Error revoking key: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error revoking API key: {str(e)}")
            raise

    @staticmethod
    def get_user_keys(user: User, include_inactive: bool = False) -> list:
        """
        Get all API keys for user.
        
        Args:
            user: User instance
            include_inactive: Include inactive/revoked keys
        
        Returns:
            List of APIKey instances
        """
        queryset = APIKey.objects.filter(user=user)
        
        if not include_inactive:
            queryset = queryset.filter(status='active')
        
        return list(queryset.order_by('-created_at'))


# Singleton instance
_api_key_service = None


def get_api_key_service() -> APIKeyService:
    """Get API key service singleton."""
    global _api_key_service
    if _api_key_service is None:
        _api_key_service = APIKeyService()
    return _api_key_service