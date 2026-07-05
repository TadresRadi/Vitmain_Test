"""
CORS configuration with security best practices.
"""
import logging
import os

logger = logging.getLogger(__name__)


class CORSConfig:
    """CORS configuration manager."""
    
    # Development CORS settings
    DEVELOPMENT_ORIGINS = [
        'http://localhost:5173',
        'http://127.0.0.1:5173',
        'http://localhost:3000',
        'http://127.0.0.1:3000',
    ]
    
    # Methods allowed in CORS requests
    ALLOWED_METHODS = [
        'GET',
        'POST',
        'PUT',
        'PATCH',
        'DELETE',
        'OPTIONS',
    ]
    
    # Headers allowed in CORS requests
    ALLOWED_HEADERS = [
        'accept',
        'accept-encoding',
        'authorization',
        'content-type',
        'dnt',
        'origin',
        'user-agent',
        'x-csrftoken',
        'x-requested-with',
    ]
    
    # Headers exposed to frontend
    EXPOSE_HEADERS = [
        'content-type',
        'x-csrftoken',
        'retry-after',
    ]
    
    @staticmethod
    def get_allowed_origins(debug: bool = False) -> list:
        """
        Get allowed CORS origins based on environment.
        
        Args:
            debug: Whether running in debug mode
        
        Returns:
            List of allowed origins
        """
        origins = []
        
        # Add development origins if debug
        if debug:
            origins.extend(CORSConfig.DEVELOPMENT_ORIGINS)
        
        # Add production origins from environment
        production_origins = os.environ.get('CORS_ALLOWED_ORIGINS', '')
        if production_origins:
            origins.extend([
                origin.strip()
                for origin in production_origins.split(',')
                if origin.strip()
            ])
        
        logger.debug(f"Allowed CORS origins: {origins}")
        return origins
    
    @staticmethod
    def validate_origin(origin: str, allowed_origins: list) -> bool:
        """
        Validate if origin is allowed.
        
        Args:
            origin: Origin from request header
            allowed_origins: List of allowed origins
        
        Returns:
            True if origin is allowed
        """
        if not origin:
            return False
        
        # Exact match
        if origin in allowed_origins:
            return True
        
        # Wildcard matching (if needed)
        # Be careful with wildcards - only use for trusted patterns
        for allowed in allowed_origins:
            if allowed.startswith('*.') and origin.endswith(allowed[1:]):
                return True
        
        return False