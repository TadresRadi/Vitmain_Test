"""
HTTPS enforcement middleware.
Redirects HTTP to HTTPS and validates secure connections.
"""
import logging
from django.conf import settings
from django.http import HttpResponsePermanentRedirect
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class HTTPSEnforcerMiddleware(MiddlewareMixin):
    """
    Enforce HTTPS in production.
    Redirects HTTP requests to HTTPS.
    """
    
    # Paths that don't require HTTPS (e.g., health check)
    EXEMPT_PATHS = [
        '/health/',
        '/metrics/',
    ]
    
    def process_request(self, request):
        """Enforce HTTPS if configured."""
        
        # Skip if not enforcing HTTPS
        if not settings.SECURE_SSL_REDIRECT:
            return None
        
        # Skip exempt paths
        if any(request.path.startswith(path) for path in self.EXEMPT_PATHS):
            return None
        
        # Skip if already HTTPS
        if request.is_secure():
            return None
        
        # Skip if explicitly disabled for this request
        if request.META.get('HTTP_X_SKIP_HTTPS_REDIRECT'):
            return None
        
        # Redirect to HTTPS
        url = request.build_absolute_uri(request.get_full_path())
        secure_url = url.replace('http://', 'https://', 1)
        
        logger.warning(f"Redirecting HTTP to HTTPS: {request.path}")
        return HttpResponsePermanentRedirect(secure_url)


class SecureProxyHeadersMiddleware(MiddlewareMixin):
    """
    Handle secure proxy headers.
    Properly detects HTTPS when behind a proxy/load balancer.
    """
    
    def process_request(self, request):
        """Process proxy headers."""
        
        # Check for proxy headers indicating HTTPS
        # These are set by reverse proxies like Nginx, CloudFlare, etc.
        proto = request.META.get('HTTP_X_FORWARDED_PROTO')
        if proto and proto.lower() == 'https':
            request.is_secure = lambda: True
        
        # Handle X-Forwarded-For for IP whitelisting
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # Get the first IP (client IP)
            client_ip = x_forwarded_for.split(',')[0].strip()
            request.client_ip = client_ip
        
        return None