"""
CSRF protection utilities.
Generates and validates CSRF tokens for OAuth and form submissions.
"""
import logging
import secrets
import hmac
from typing import Optional, Tuple
from django.core.cache import cache

logger = logging.getLogger(__name__)

CSRF_TOKEN_LENGTH = 32
CSRF_TOKEN_TTL = 3600  # 1 hour
CSRF_CACHE_PREFIX = "csrf_token:"


class CSRFTokenManager:
    """Manage CSRF token generation and validation."""
    
    @staticmethod
    def generate_token() -> str:
        """
        Generate a cryptographically secure CSRF token.
        
        Returns:
            32-byte hex string token
        """
        token = secrets.token_hex(CSRF_TOKEN_LENGTH // 2)
        # Do NOT log token prefixes — log only that a token was generated.
        logger.debug("Generated CSRF token")
        return token
    
    @staticmethod
    def store_token(token: str, request_id: str) -> bool:
        """
        Store CSRF token in cache with request identifier.
        
        Args:
            token: The CSRF token
            request_id: Unique request identifier (session, user ID, or request hash)
        
        Returns:
            True if stored successfully
        """
        try:
            cache_key = f"{CSRF_CACHE_PREFIX}{request_id}"
            cache.set(cache_key, token, CSRF_TOKEN_TTL)
            logger.debug(f"Stored CSRF token for request: {request_id}")
            return True
        except Exception as e:
            logger.error(f"Error storing CSRF token: {str(e)}")
            return False
    
    @staticmethod
    def validate_token(token: str, request_id: str) -> bool:
        """
        Validate CSRF token against stored value.
        
        Args:
            token: Token from request
            request_id: Request identifier
        
        Returns:
            True if token is valid and not expired
        """
        try:
            if not token or not isinstance(token, str):
                logger.warning("Invalid CSRF token format")
                return False
            
            cache_key = f"{CSRF_CACHE_PREFIX}{request_id}"
            stored_token = cache.get(cache_key)
            
            if not stored_token:
                logger.warning(f"No stored token for request: {request_id}")
                return False
            
            # Use timing-safe comparison to prevent timing attacks
            if not CSRFTokenManager._constant_time_compare(token, stored_token):
                logger.warning(f"CSRF token mismatch for request: {request_id}")
                return False
            
            # Delete token after validation (one-time use)
            cache.delete(cache_key)
            logger.debug(f"Valid CSRF token for request: {request_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error validating CSRF token: {str(e)}")
            return False
    
    @staticmethod
    def _constant_time_compare(a: str, b: str) -> bool:
        """
        Compare two strings in constant time to prevent timing attacks.
        
        Args:
            a: First string
            b: Second string
        
        Returns:
            True if strings are equal
        """
        return hmac.compare_digest(a, b)
    
    @staticmethod
    def revoke_token(request_id: str) -> bool:
        """
        Revoke/delete a CSRF token immediately.
        
        Args:
            request_id: Request identifier
        
        Returns:
            True if revoked
        """
        try:
            cache_key = f"{CSRF_CACHE_PREFIX}{request_id}"
            cache.delete(cache_key)
            logger.info(f"Revoked CSRF token for request: {request_id}")
            return True
        except Exception as e:
            logger.error(f"Error revoking CSRF token: {str(e)}")
            return False


class OAuthStateManager:
    """Manage OAuth state parameter for CSRF protection in OAuth flows."""
    
    STATE_PREFIX = "oauth_state:"
    STATE_TTL = 600  # 10 minutes
    
    @staticmethod
    def generate_state(user_id: Optional[str] = None) -> str:
        """
        Generate OAuth state parameter.
        Prevents CSRF attacks in OAuth flow.
        
        Args:
            user_id: Optional user ID for state binding
        
        Returns:
            State parameter string
        """
        state = secrets.token_urlsafe(32)
        logger.debug(f"Generated OAuth state: {state[:8]}...")
        return state
    
    @staticmethod
    def store_state(state: str, request_id: str, metadata: dict = None) -> bool:
        """
        Store state in cache with metadata.
        
        Args:
            state: State parameter
            request_id: Request/session identifier
            metadata: Optional metadata (user_id, nonce, etc.)
        
        Returns:
            True if stored
        """
        try:
            cache_key = f"{OAuthStateManager.STATE_PREFIX}{state}"
            data = {
                'request_id': request_id,
                'metadata': metadata or {},
            }
            cache.set(cache_key, data, OAuthStateManager.STATE_TTL)
            logger.debug(f"Stored OAuth state: {state[:8]}...")
            return True
        except Exception as e:
            logger.error(f"Error storing OAuth state: {str(e)}")
            return False
    
    @staticmethod
    def validate_state(state: str, request_id: str) -> Tuple[bool, dict]:
        """
        Validate OAuth state parameter.
        
        Args:
            state: State from OAuth callback
            request_id: Request/session identifier
        
        Returns:
            Tuple of (is_valid, metadata)
        """
        try:
            if not state or not isinstance(state, str):
                logger.warning("Invalid OAuth state format")
                return False, {}
            
            cache_key = f"{OAuthStateManager.STATE_PREFIX}{state}"
            data = cache.get(cache_key)
            
            if not data:
                logger.warning(f"OAuth state not found or expired: {state[:8]}...")
                return False, {}
            
            # Verify request ID matches
            if data.get('request_id') != request_id:
                logger.warning("OAuth state request_id mismatch")
                return False, {}
            
            # Delete state after validation (one-time use)
            cache.delete(cache_key)
            logger.debug(f"Valid OAuth state: {state[:8]}...")
            return True, data.get('metadata', {})
        
        except Exception as e:
            logger.error(f"Error validating OAuth state: {str(e)}")
            return False, {}


# Singleton instances
_csrf_manager = None
_state_manager = None


def get_csrf_manager() -> CSRFTokenManager:
    """Get CSRF token manager singleton."""
    global _csrf_manager
    if _csrf_manager is None:
        _csrf_manager = CSRFTokenManager()
    return _csrf_manager


def get_state_manager() -> OAuthStateManager:
    """Get OAuth state manager singleton."""
    global _state_manager
    if _state_manager is None:
        _state_manager = OAuthStateManager()
    return _state_manager