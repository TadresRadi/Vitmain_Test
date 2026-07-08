"""
Custom decorators for views.
"""
import logging
from functools import wraps
from django.core.cache import cache
from rest_framework import status
from rest_framework.response import Response

logger = logging.getLogger(__name__)


def ratelimit(key='ip', rate='100/h'):
    """
    Rate limit decorator for views.
    
    Args:
        key: 'ip' or 'user'
        rate: Format like '10/m' (10 per minute), '100/h' (100 per hour)
    
    Example:
        @ratelimit(key='ip', rate='10/m')
        def my_view(request):
            ...
    """
    # Parse rate
    limit, period = rate.split('/')
    limit = int(limit)
    
    period_seconds = {
        's': 1,
        'm': 60,
        'h': 3600,
        'd': 86400,
    }
    period_sec = period_seconds.get(period[-1], 3600)
    
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(self, request, *args, **kwargs):
            # Get identifier
            if key == 'ip':
                identifier = self._get_client_ip(request)
            elif key == 'user':
                identifier = str(request.user.id) if request.user.is_authenticated else 'anon'
            else:
                identifier = 'unknown'
            
            cache_key = f"ratelimit:{view_func.__name__}:{identifier}"
            
            # Check rate limit
            current = cache.get(cache_key, 0)
            if current >= limit:
                logger.warning(f"Rate limit exceeded for {identifier}")
                return Response(
                    {'error': 'rate_limit', 'message': 'Too many requests'},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )
            
            # Increment counter
            cache.set(cache_key, current + 1, period_sec)
            
            # Call original view
            return view_func(self, request, *args, **kwargs)
        
        return wrapper
    return decorator


def _get_client_ip(request):
    """Get client IP from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def rate_limit(endpoint: str, rate: str = None):
    """
    Rate limit decorator for views.
    
    Args:
        endpoint: Endpoint identifier (for logging and config)
        rate: Optional rate limit override (e.g., '10/m')
    
    Example:
        @rate_limit(endpoint='auth_login', rate='5/m')
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(self, request, *args, **kwargs):
            from core.rate_limit import RateLimiter
            
            # Check rate limit
            is_limited, retry_after = RateLimiter.is_rate_limited(
                request, endpoint, rate
            )
            
            if is_limited:
                return RateLimiter.get_rate_limit_response(retry_after)
            
            # Call original view
            return view_func(self, request, *args, **kwargs)
        
        return wrapper
    return decorator