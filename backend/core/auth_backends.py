"""
API Key authentication backend.
"""
import logging
from typing import Optional, Tuple
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model
from core.api_key_models import APIKey
from core.api_key_service import API_KEY_PREFIX
from core.api_key_service import get_api_key_service
from core.metrics import inc_api_key_usage

User = get_user_model()
logger = logging.getLogger(__name__)


class APIKeyAuthentication(TokenAuthentication):
    """
    API Key authentication.
    
    Usage in requests:
        Authorization: Bearer vitmain_xxxxx
    or
        X-API-Key: vitmain_xxxxx
    """
    
    keyword = 'Bearer'
    model = APIKey

    def get_model(self):
        """Return the model to use."""
        return APIKey

    def authenticate(self, request) -> Optional[Tuple[User, APIKey]]:
        """
        Authenticate using API key.

        Checks both Authorization header and X-API-Key header.

        If the Authorization header contains a Bearer token that does NOT
        start with the API key prefix ('vitmain_'), this method returns
        None so that the next authentication class (JWTAuthentication)
        can handle it. This is critical because DRF stops at the first
        AuthenticationFailed — if we raised here, JWT auth would never run.
        """
        # Try Authorization header first
        auth = request.META.get('HTTP_AUTHORIZATION', '').split()

        if auth and auth[0].lower() == 'bearer':
            if len(auth) == 1:
                msg = 'Invalid token header. No credentials provided.'
                raise AuthenticationFailed(msg)
            elif len(auth) > 2:
                msg = 'Invalid token header. Token string should not contain spaces.'
                raise AuthenticationFailed(msg)

            token = auth[1]

            # If the Bearer token doesn't look like an API key, return None
            # so JWTAuthentication can try to decode it as a JWT.
            # Raising here would block JWT auth entirely.
            if not token.startswith(API_KEY_PREFIX):
                return None

        else:
            # Try X-API-Key header
            token = request.META.get('HTTP_X_API_KEY')

            if not token:
                return None  # No API key provided

        return self.authenticate_credentials(token, request)

    def authenticate_credentials(self, key: str, request) -> Tuple[User, APIKey]:
        """
        Authenticate the key string.
        """
        api_key_service = get_api_key_service()

        # Get client IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')

        # Authenticate with service
        api_key = api_key_service.authenticate_with_key(key, ip)

        if not api_key:
            raise AuthenticationFailed('Invalid or inactive API key.')

        if not api_key.user.is_active:
            raise AuthenticationFailed('User inactive or deleted.')

        # Track API key usage in Prometheus metrics
        # Use the key prefix (first 32 chars) as identifier — never the full key
        endpoint = request.path
        inc_api_key_usage(api_key.key_prefix, endpoint)

        # Check permissions based on scope
        request.api_key = api_key
        request.api_key_scope = api_key.scope

        return (api_key.user, api_key)