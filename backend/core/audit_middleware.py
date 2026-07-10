"""
Middleware for automatic audit logging.
Captures request/response info for audit trail.
"""
import logging
import json
from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from core.audit_service import get_audit_logger
from core.http_utils import get_client_ip


logger = logging.getLogger(__name__)


class AuditLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log all requests for audit trail.
    Captures IP, user agent, and request details.
    """

    # Endpoints to skip logging (to avoid noise)
    SKIP_PATHS = [
        '/health/',
        '/metrics/',
        '/static/',
        '/media/',
    ]

    # Sensitive endpoints to log extra details
    SENSITIVE_PATHS = [
        '/api/auth/',
        '/api/users/',
        '/api/admin/',
    ]

    def process_request(self, request):
        """Capture request info."""
        # Skip certain paths
        if any(request.path.startswith(path) for path in self.SKIP_PATHS):
            return None

        # Store request info for response processing
        request._start_time = timezone.now()
        request._request_path = request.path
        request._request_method = request.method

        return None

    def process_response(self, request, response):
        """Log response for audit trail."""
        # Skip if request was skipped
        if any(request.path.startswith(path) for path in self.SKIP_PATHS):
            return response

        try:
            # Get request details
            user_ip = get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
            user = request.user if request.user.is_authenticated else None
            user_email = user.email if user else 'anonymous'

            # Determine if sensitive endpoint
            is_sensitive = any(
                request.path.startswith(path) for path in self.SENSITIVE_PATHS
            )

            # Only log sensitive endpoints and errors
            if is_sensitive or response.status_code >= 400:
                logger.info(
                    f"Request logged - {request.method} {request.path} - "
                    f"Status: {response.status_code} - User: {user_email} - IP: {user_ip}"
                )

        except Exception as e:
            logger.error(f"Error in audit logging middleware: {str(e)}")

        return response