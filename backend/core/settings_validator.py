"""
Validate security settings are properly configured.
Run at startup to catch configuration issues early.
"""
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class SettingsValidator:
    """Validate Django settings for security."""
    
    WARNINGS = []
    ERRORS = []
    
    @classmethod
    def validate(cls) -> bool:
        """
        Validate all security settings.
        
        Returns:
            True if all critical validations pass
        """
        cls.WARNINGS = []
        cls.ERRORS = []
        
        # Run all validators
        cls._validate_https()
        cls._validate_cookies()
        cls._validate_csrf()
        cls._validate_cors()
        cls._validate_database()
        cls._validate_cache()
        cls._validate_secrets()
        
        # Log results
        if cls.ERRORS:
            logger.error("=" * 80)
            logger.error("SECURITY CONFIGURATION ERRORS:")
            for error in cls.ERRORS:
                logger.error(f"  ❌ {error}")
            logger.error("=" * 80)
            return False
        
        if cls.WARNINGS:
            logger.warning("=" * 80)
            logger.warning("SECURITY CONFIGURATION WARNINGS:")
            for warning in cls.WARNINGS:
                logger.warning(f"  ⚠️  {warning}")
            logger.warning("=" * 80)
        
        return True
    
    @classmethod
    def _validate_https(cls):
        """Validate HTTPS configuration."""
        if not settings.DEBUG:
            if not settings.SECURE_SSL_REDIRECT:
                cls.ERRORS.append(
                    "SECURE_SSL_REDIRECT should be True in production"
                )
            
            if settings.SECURE_HSTS_SECONDS < 31536000:
                cls.WARNINGS.append(
                    f"SECURE_HSTS_SECONDS is {settings.SECURE_HSTS_SECONDS}, "
                    f"recommended is 31536000 (1 year)"
                )
    
    @classmethod
    def _validate_cookies(cls):
        """Validate cookie security settings."""
        if not settings.DEBUG:
            if not settings.SESSION_COOKIE_SECURE:
                cls.ERRORS.append(
                    "SESSION_COOKIE_SECURE should be True in production"
                )
            
            if not settings.CSRF_COOKIE_SECURE:
                cls.ERRORS.append(
                    "CSRF_COOKIE_SECURE should be True in production"
                )
            
            if not settings.SESSION_COOKIE_HTTPONLY:
                cls.WARNINGS.append(
                    "SESSION_COOKIE_HTTPONLY is not set (should be True)"
                )
    
    @classmethod
    def _validate_csrf(cls):
        """Validate CSRF protection."""
        if settings.DEBUG:
            cls.WARNINGS.append(
                "DEBUG=true - CSRF protection is relaxed"
            )
        
        if not settings.CSRF_TRUSTED_ORIGINS:
            cls.WARNINGS.append(
                "CSRF_TRUSTED_ORIGINS is not configured"
            )
    
    @classmethod
    def _validate_cors(cls):
        """Validate CORS configuration."""
        if settings.CORS_ALLOW_ALL_ORIGINS and not settings.DEBUG:
            cls.ERRORS.append(
                "CORS_ALLOW_ALL_ORIGINS should not be True in production"
            )
        
        if not settings.CORS_ALLOWED_ORIGINS and not settings.DEBUG:
            cls.WARNINGS.append(
                "CORS_ALLOWED_ORIGINS is empty in production"
            )
    
    @classmethod
    def _validate_database(cls):
        """Validate database security."""
        db_password = settings.DATABASES['default'].get('PASSWORD', '')
        
        if not db_password:
            cls.WARNINGS.append(
                "Database password is empty or not set"
            )
        
        if db_password == 'password' or db_password == 'postgres':  # nosec B105 - comparing against known weak defaults
            cls.ERRORS.append(
                "Database password is using default/weak value"
            )
        
        if settings.DATABASES['default']['HOST'] == 'localhost' and not settings.DEBUG:
            cls.WARNINGS.append(
                "Database host is localhost in production"
            )
    
    @classmethod
    def _validate_cache(cls):
        """Validate cache configuration."""
        cache_backend = settings.CACHES['default']['BACKEND']
        
        if 'LocMemCache' in cache_backend and not settings.DEBUG:
            cls.WARNINGS.append(
                "Using local memory cache in production (not recommended). "
                "Use Redis for distributed caching."
            )
    
    @classmethod
    def _validate_secrets(cls):
        """Validate secret key and credentials."""
        secret_key = settings.SECRET_KEY
        
        if not secret_key or secret_key == 'dev-secret-key':  # nosec B105 - comparing against known weak default
            cls.ERRORS.append(
                "SECRET_KEY is not set or using development value"
            )
        
        if len(secret_key) < 50:
            cls.WARNINGS.append(
                "SECRET_KEY is shorter than recommended (min 50 characters)"
            )
        
        if not settings.GOOGLE_CLIENT_ID:
            cls.WARNINGS.append(
                "Google OAuth client ID is not configured"
            )
