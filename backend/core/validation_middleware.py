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
    
    # JSON/form requests are limited to 1MB.
    # File uploads (multipart/form-data) get a much higher limit
    # because images and videos are typically 2-50MB.
    MAX_REQUEST_SIZE = 1024 * 1024  # 1MB for JSON
    MAX_FILE_UPLOAD_SIZE = 50 * 1024 * 1024  # 50MB for multipart (images/videos)
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
        # Check content length for non-GET requests
        if request.method != 'GET':
            content_length = request.META.get('CONTENT_LENGTH', 0)
            try:
                content_length = int(content_length)
                
                # Use a higher size limit for multipart/form-data (file uploads)
                content_type = request.META.get('CONTENT_TYPE', '').split(';')[0].strip()
                if content_type == 'multipart/form-data':
                    max_size = self.MAX_FILE_UPLOAD_SIZE
                else:
                    max_size = self.MAX_REQUEST_SIZE
                
                if content_length > max_size:
                    logger.warning(
                        f"Request too large: {content_length} > {max_size} "
                        f"(content_type: {content_type})"
                    )
                    return JsonResponse(
                        {'error': 'request_too_large', 'message': f'Request body too large. Maximum allowed: {max_size // (1024*1024)}MB'},
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