"""
Custom exceptions for the application.
"""
from rest_framework import status
from rest_framework.exceptions import APIException


class VitmainAPIException(APIException):
    """Base exception for Vitmain API."""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "An error occurred"
    default_code = "error"


class AuthenticationError(VitmainAPIException):
    """Authentication failed."""
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Authentication failed"
    default_code = "authentication_error"


class AuthorizationError(VitmainAPIException):
    """User is not authorized."""
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "You do not have permission to perform this action"
    default_code = "authorization_error"


class ValidationError(VitmainAPIException):
    """Validation error."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Invalid input"
    default_code = "validation_error"


class NotFoundError(VitmainAPIException):
    """Resource not found."""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Resource not found"
    default_code = "not_found"


class ConflictError(VitmainAPIException):
    """Resource conflict."""
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Resource conflict"
    default_code = "conflict"


class ExternalServiceError(VitmainAPIException):
    """External service error."""
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = "External service unavailable"
    default_code = "service_unavailable"


class RateLimitError(VitmainAPIException):
    """Rate limit exceeded."""
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = "Rate limit exceeded"
    default_code = "rate_limit"