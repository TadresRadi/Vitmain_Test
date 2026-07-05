"""
Exception handlers for API responses.
"""
import logging
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import APIException
from core.exceptions import VitmainAPIException

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that returns consistent error format.
    
    Error Response Format:
    {
        "error": "error_code",
        "message": "Human readable message",
        "detail": "Additional details if available"
    }
    """
    
    # Get request and view for logging
    request = context.get('request')
    view = context.get('view')
    
    # Handle VitmainAPIException and DRF exceptions
    if isinstance(exc, VitmainAPIException):
        status_code = exc.status_code
        error_code = exc.default_code
        message = str(exc.detail) if hasattr(exc, 'detail') else exc.default_detail
    elif isinstance(exc, APIException):
        status_code = exc.status_code
        error_code = getattr(exc, 'default_code', 'error')
        message = str(exc.detail) if hasattr(exc, 'detail') else 'An error occurred'
    else:
        # Unhandled exception
        logger.exception(f"Unhandled exception in {view}", exc_info=exc)
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        error_code = 'internal_error'
        message = 'Internal server error'
    
    # Log the error
    log_level = 'error' if status_code >= 500 else 'warning'
    getattr(logger, log_level)(
        f"{request.method} {request.path} - {status_code} {error_code}: {message}",
        extra={
            'status_code': status_code,
            'error_code': error_code,
            'user_id': getattr(request.user, 'id', None),
        }
    )
    
    response_data = {
        'error': error_code,
        'message': message,
    }
    
    return Response(response_data, status=status_code)