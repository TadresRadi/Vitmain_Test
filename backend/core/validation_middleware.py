"""
Request validation middleware.
Validates and sanitizes incoming requests.
"""
import logging
import json
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from rest_framework import status

logger = logging.getLogger(__name__)


class RequestValidationMiddleware(MiddlewareMixin):
    """
    Middleware for validating incoming requests.
    - Checks content-type
    - Limits request size
    - Validates JSON format
    """
    
    MAX_REQUEST_SIZE = 1024 * 1024  # 1MB
    ALLOWED_CONTENT_TYPES = [
        'application/json',
        'application/x-www-form-urlencoded',
        'multipart/form-data',
    ]
    
    def process_request(self, request):
        """Validate incoming request."""
        
        # Check request method
        if request.method not in ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS']:
            logger.warning(f"Invalid HTTP method: {request.method}")
            return JsonResponse(
                {'error': 'invalid_method', 'message': 'Invalid HTTP method'},
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        
        # Check content length for non-GET requests
        if request.method != 'GET':
            content_length = request.META.get('CONTENT_LENGTH', 0)
            try:
                content_length = int(content_length)
                if content_length > self.MAX_REQUEST_SIZE:
                    logger.warning(
                        f"Request too large: {content_length} > {self.MAX_REQUEST_SIZE}"
                    )
                    return JsonResponse(
                        {'error': 'request_too_large', 'message': 'Request body too large'},
                        status=status.HTTP_413_PAYLOAD_TOO_LARGE
                    )
            except (ValueError, TypeError):
                logger.warning("Invalid content length header")
        
        # Validate JSON for JSON requests
        if request.method in ['POST', 'PUT', 'PATCH']:
            content_type = request.META.get('CONTENT_TYPE', '').split(';')[0]
            if 'json' in content_type.lower():
                try:
                    json.loads(request.body.decode('utf-8'))
                except (json.JSONDecodeError, UnicodeDecodeError) as e:
                    logger.warning(f"Invalid JSON in request: {str(e)}")
                    return JsonResponse(
                        {'error': 'invalid_json', 'message': 'Invalid JSON format'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
        
        return None