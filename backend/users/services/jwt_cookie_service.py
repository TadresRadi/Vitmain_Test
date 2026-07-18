"""
JWT cookie service.
Manages setting and clearing the httpOnly refresh token cookie.
"""
from django.conf import settings


def set_jwt_refresh_cookie(response, refresh_token):
    """
    Set the refresh token as an httpOnly cookie on the response.

    The cookie is:
    - httpOnly: not accessible via JavaScript
    - secure: only sent over HTTPS (when DEBUG=False)
    - samesite=Lax: prevents CSRF from cross-site requests
    - Path=/: available on all endpoints
    """
    response.set_cookie(
        settings.JWT_AUTH_COOKIE,
        refresh_token,
        httponly=settings.JWT_AUTH_COOKIE_HTTPONLY,
        secure=settings.JWT_AUTH_COOKIE_SECURE,
        samesite=settings.JWT_AUTH_COOKIE_SAMESITE,
        path=settings.JWT_AUTH_COOKIE_PATH,
        domain=settings.JWT_AUTH_COOKIE_DOMAIN,
        max_age=int(settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds()),
    )
    return response


def clear_jwt_refresh_cookie(response):
    """Clear the refresh token cookie."""
    response.delete_cookie(
        settings.JWT_AUTH_COOKIE,
        path=settings.JWT_AUTH_COOKIE_PATH,
        domain=settings.JWT_AUTH_COOKIE_DOMAIN,
    )
    return response


def get_refresh_token_from_cookie(request):
    """Read the refresh token from the request cookie."""
    return request.COOKIES.get(settings.JWT_AUTH_COOKIE)