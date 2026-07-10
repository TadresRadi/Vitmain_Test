"""
Custom decorators for views.
"""
import logging
from functools import wraps

logger = logging.getLogger(__name__)


def rate_limit(endpoint: str, rate: str = None):
    """
    Rate limit decorator for class-based views.

    Uses the RateLimiter class (core.rate_limit) which implements a
    sliding-window algorithm backed by Django's cache (Redis in prod).

    Args:
        endpoint: Endpoint identifier (for logging and config). If a
            default rate exists in RateLimitConfig.ENDPOINTS for this
            endpoint, the `rate` argument is optional.
        rate: Optional rate limit override (e.g., '10/m', '100/h').
            If None, uses the default from RateLimitConfig.ENDPOINTS,
            falling back to '100/h' (api_default).

    Example:
        @rate_limit(endpoint='auth_login', rate='5/m')
        def post(self, request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(self, request, *args, **kwargs):
            from core.rate_limit import RateLimiter

            is_limited, retry_after = RateLimiter.is_rate_limited(
                request, endpoint, rate
            )

            if is_limited:
                return RateLimiter.get_rate_limit_response(retry_after)

            return view_func(self, request, *args, **kwargs)

        return wrapper
    return decorator