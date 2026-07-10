"""
Shared HTTP utility functions.
"""
from django.http import HttpRequest


def get_client_ip(request: HttpRequest) -> str:
    """
    Extract the client IP address from a Django request.

    Checks the X-Forwarded-For header first (set by proxies/load balancers),
    falling back to REMOTE_ADDR. The first IP in X-Forwarded-For is the
    original client.

    Args:
        request: Django HttpRequest object.

    Returns:
        The client IP address as a string, or 'unknown' if it cannot be
        determined.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # X-Forwarded-For can be a comma-separated list: "client, proxy1, proxy2"
        # The first entry is the original client IP.
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', 'unknown')