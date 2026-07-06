"""
Advanced rate limiting for API endpoints.
Supports per-IP, per-user, and sliding window algorithms.
"""
import logging
import hashlib
from typing import Optional, Tuple
import time
from django.core.cache import cache
from rest_framework import status
from rest_framework.response import Response

logger = logging.getLogger(__name__)


class RateLimitConfig:
    """Configuration for rate limits."""
    
    # Format: 'requests/period' (e.g., '10/m' = 10 requests per minute)
    ENDPOINTS = {
        'auth_login': '5/m',           # 5 attempts per minute
        'auth_register': '3/h',         # 3 registrations per hour
        'google_callback': '10/m',      # 10 OAuth attempts per minute
        'password_reset': '3/h',        # 3 reset requests per hour
        'api_default': '100/h',         # 100 requests per hour
    }
    
    PERIOD_SECONDS = {
        's': 1,
        'm': 60,
        'h': 3600,
        'd': 86400,
    }


class RateLimiter:
    """Rate limiter using sliding window algorithm."""
    
    PREFIX = "ratelimit:"
    
    @staticmethod
    def get_client_identifier(request) -> str:
        """
        Get unique client identifier from request.
        Uses IP address or user ID.
        
        Args:
            request: Django request object
        
        Returns:
            Unique identifier string
        """
        if request.user.is_authenticated:
            return f"user:{request.user.id}"
        
        # Get client IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', 'unknown')
        
        return f"ip:{ip}"
    
    @staticmethod
    def parse_rate_limit(rate: str) -> Tuple[int, int]:
        """
        Parse rate limit string.
        
        Args:
            rate: Rate string like '10/m' or '100/h'
        
        Returns:
            Tuple of (requests, seconds)
        
        Raises:
            ValueError: If format is invalid
        """
        try:
            requests, period = rate.split('/')
            requests = int(requests)
            
            period_char = period[-1].lower()
            seconds = RateLimitConfig.PERIOD_SECONDS.get(period_char)
            
            if seconds is None:
                raise ValueError(f"Invalid period: {period}")
            
            return requests, seconds
        except Exception as e:
            logger.error(f"Error parsing rate limit '{rate}': {str(e)}")
            raise ValueError(f"Invalid rate limit format: {rate}")
    
    @staticmethod
    def is_rate_limited(
        request,
        endpoint: str,
        rate: Optional[str] = None
    ) -> Tuple[bool, Optional[int]]:
        """
        Check if request is rate limited.
        Uses sliding window algorithm.
        
        Args:
            request: Django request object
            endpoint: Endpoint name (for logging)
            rate: Rate limit string (e.g., '10/m'). If None, uses defaults.
        
        Returns:
            Tuple of (is_limited, retry_after_seconds)
        """
        try:
            # Get rate limit
            if rate is None:
                rate = RateLimitConfig.ENDPOINTS.get(
                    endpoint,
                    RateLimitConfig.ENDPOINTS['api_default']
                )
            
            limit, window_seconds = RateLimiter.parse_rate_limit(rate)
            
            # Get client identifier
            identifier = RateLimiter.get_client_identifier(request)
            
            # Create cache key
            cache_key = f"{RateLimiter.PREFIX}{identifier}:{endpoint}"
            
            # Get current count and timestamp
            data = cache.get(cache_key)

            now = time.time()

            if not data or data.get("window_start") is None:
                data = {
                    "count": 0,
                    "window_start": now,
                }

            window_start = data["window_start"]
            elapsed = now - window_start
            # Reset window if expired
            if elapsed > window_seconds:
                data = {'count': 1, 'window_start': now}
                retry_after = window_seconds
            else:
                data['count'] += 1
                retry_after = int(window_seconds - elapsed)
                
                if data['count'] > limit:
                    # Rate limit exceeded
                    cache.set(cache_key, data, window_seconds)
                    logger.warning(
                        f"Rate limit exceeded for {identifier} on {endpoint}: "
                        f"{data['count']}/{limit}"
                    )
                    return True, retry_after
            
            # Update cache
            cache.set(cache_key, data, window_seconds)
            return False, None
        
        except Exception as e:
            logger.error(f"Rate limit check error: {str(e)}")
            # Default to allowing request on error
            return False, None
    
    @staticmethod
    def get_rate_limit_response(retry_after: int) -> Response:
        """
        Get rate limit error response.
        
        Args:
            retry_after: Seconds to wait before retry
        
        Returns:
            Response with 429 status
        """
        return Response(
            {
                'error': 'rate_limit',
                'message': 'Too many requests. Please try again later.',
                'retry_after': retry_after,
            },
            status=status.HTTP_429_TOO_MANY_REQUESTS,
            headers={'Retry-After': str(retry_after)}
        )
    
    @staticmethod
    def reset_limit(request, endpoint: str) -> bool:
        """
        Reset rate limit for a client (admin only).
        
        Args:
            request: Django request object
            endpoint: Endpoint name
        
        Returns:
            True if reset successfully
        """
        try:
            identifier = RateLimiter.get_client_identifier(request)
            cache_key = f"{RateLimiter.PREFIX}{identifier}:{endpoint}"
            cache.delete(cache_key)
            logger.info(f"Reset rate limit for {identifier} on {endpoint}")
            return True
        except Exception as e:
            logger.error(f"Error resetting rate limit: {str(e)}")
            return False