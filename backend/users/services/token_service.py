"""
Token management service.
Handles token generation, validation, and blacklisting.
"""
import logging
from typing import Optional, Dict, Any
from django.core.cache import cache
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.contrib.auth import get_user_model

User = get_user_model()
logger = logging.getLogger(__name__)

TOKEN_BLACKLIST_PREFIX = "token_blacklist:"
TOKEN_REFRESH_ROTATION_KEY = "token_rotation:"


class TokenService:
    """Service for managing JWT tokens."""
    
    @staticmethod
    def generate_tokens(user: User) -> Dict[str, str]:
        """
        Generate JWT access and refresh tokens for user.
        
        Args:
            user: User instance
        
        Returns:
            Dict with access_token and refresh_token
        
        Raises:
            Exception: If token generation fails
        """
        try:
            refresh = RefreshToken.for_user(user)
            
            # Add custom claims
            refresh['email'] = user.email
            refresh['role'] = user.role
            
            return {
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
            }
        except Exception as e:
            logger.error(f"Error generating tokens: {str(e)}")
            raise
    
    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """
        Verify JWT token and return payload.
        
        Args:
            token: JWT token string
        
        Returns:
            Token payload dict if valid, None otherwise
        """
        try:
            from rest_framework_simplejwt.backends import TokenBackend
            backend = TokenBackend(algorithm='HS256')
            validated_payload = backend.decode(token, verify=True)
            return validated_payload
        except TokenError as e:
            logger.warning(f"Invalid token: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error verifying token: {str(e)}")
            return None
    
    @staticmethod
    def blacklist_token(token: str) -> bool:
        """
        Blacklist a token (logout).
        Prevents token from being used after logout.
        
        Args:
            token: JWT token string
        
        Returns:
            True if blacklisted successfully
        """
        try:
            payload = TokenService.verify_token(token)
            if not payload:
                logger.warning("Cannot blacklist invalid token")
                return False
            
            # Get token expiration time
            exp_timestamp = payload.get('exp')
            if not exp_timestamp:
                logger.warning("Token has no expiration")
                return False
            
            # Calculate TTL (token expiration minus now)
            from datetime import datetime
            exp_time = datetime.fromtimestamp(exp_timestamp)
            now = datetime.utcnow()
            ttl = int((exp_time - now).total_seconds())
            
            if ttl <= 0:
                logger.debug("Token already expired, no need to blacklist")
                return True
            
            # Add to blacklist with TTL
            cache_key = f"{TOKEN_BLACKLIST_PREFIX}{token}"
            cache.set(cache_key, True, ttl)
            logger.info(f"Token blacklisted for {ttl} seconds")
            return True
        
        except Exception as e:
            logger.error(f"Error blacklisting token: {str(e)}")
            return False
    
    @staticmethod
    def is_token_blacklisted(token: str) -> bool:
        """
        Check if token is blacklisted.
        
        Args:
            token: JWT token string
        
        Returns:
            True if token is blacklisted
        """
        try:
            cache_key = f"{TOKEN_BLACKLIST_PREFIX}{token}"
            return cache.get(cache_key, False)
        except Exception as e:
            logger.error(f"Error checking token blacklist: {str(e)}")
            return False
    
    @staticmethod
    def refresh_with_rotation(refresh_token: str) -> Optional[Dict[str, str]]:
        """
        Refresh access token with rotation.
        Implements refresh token rotation for enhanced security.
        
        Args:
            refresh_token: Refresh token string
        
        Returns:
            Dict with new tokens or None
        """
        try:
            # Check if refresh token is blacklisted
            if TokenService.is_token_blacklisted(refresh_token):
                logger.warning("Attempted to use blacklisted refresh token")
                return None
            
            # Create new tokens
            refresh = RefreshToken(refresh_token)
            new_refresh = refresh.rotate()
            
            # Blacklist old refresh token
            TokenService.blacklist_token(refresh_token)
            
            return {
                'access_token': str(new_refresh.access_token),
                'refresh_token': str(new_refresh),
            }
        except TokenError as e:
            logger.warning(f"Invalid refresh token: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error refreshing token: {str(e)}")
            return None


# Singleton instance
_token_service = None


def get_token_service() -> TokenService:
    """Get token service singleton."""
    global _token_service
    if _token_service is None:
        _token_service = TokenService()
    return _token_service