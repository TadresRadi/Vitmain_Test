"""
Security headers middleware.
Adds HTTP security headers to all responses.
"""
import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Add security-related HTTP headers to responses.
    
    Headers added:
    - Strict-Transport-Security (HSTS)
    - X-Content-Type-Options
    - X-Frame-Options
    - X-XSS-Protection
    - Referrer-Policy
    - Content-Security-Policy
    - Permissions-Policy
    """
    
    def process_response(self, request, response):
        """Add security headers to response."""
        
        # Strict-Transport-Security (HSTS)
        # Forces HTTPS for 1 year, including subdomains
        response['Strict-Transport-Security'] = (
            'max-age=31536000; includeSubDomains; preload'
        )
        
        # X-Content-Type-Options
        # Prevents MIME type sniffing attacks
        response['X-Content-Type-Options'] = 'nosniff'
        
        # X-Frame-Options
        # Prevents clickjacking attacks
        # DENY: Page cannot be displayed in a frame
        response['X-Frame-Options'] = 'DENY'
        
        # X-XSS-Protection
        # Enables browser XSS protection (older browsers)
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Referrer-Policy
        # Controls how much referrer info is shared
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Permissions-Policy (formerly Feature-Policy)
        # Controls which browser features can be used
        response['Permissions-Policy'] = (
            'accelerometer=(), '
            'camera=(), '
            'geolocation=(), '
            'gyroscope=(), '
            'magnetometer=(), '
            'microphone=(), '
            'payment=(), '
            'usb=()'
        )
        
        return response


class CSPHeaderMiddleware(MiddlewareMixin):
    """
    Content-Security-Policy header middleware.
    Prevents XSS and injection attacks.
    """
    
    # CSP directives
    CSP_DIRECTIVES = {
        'default-src': ["'self'"],
        'script-src': [
            "'self'",
            "'unsafe-inline'",  # Only if necessary - can be removed
            'https://accounts.google.com',
            'https://*.googleapis.com',
            'https://cdn.jsdelivr.net',
        ],
        'style-src': [
            "'self'",
            "'unsafe-inline'",  # Tailwind/CSS requires this
            'https://fonts.googleapis.com',
            'https://cdn.jsdelivr.net',
        ],
        'img-src': [
            "'self'",
            'https:',
            'data:',  # Allow data URIs for images
        ],
        'font-src': [
            "'self'",
            'https://fonts.gstatic.com',
            'https://cdn.jsdelivr.net',
        ],
        'connect-src': [
            "'self'",
            'https://oauth2.googleapis.com',
            'https://tokeninfo.googleapis.com',
            'https://accounts.google.com',
        ],
        'frame-src': [
            "'self'",
            'https://accounts.google.com',
        ],
        'object-src': ["'none'"],
        'base-uri': ["'self'"],
        'form-action': ["'self'"],
        'frame-ancestors': ["'none'"],
        'upgrade-insecure-requests': [],
    }
    
    def process_response(self, request, response):
        """Add Content-Security-Policy header."""
        
        # Build CSP header value
        csp_parts = []
        for directive, sources in self.CSP_DIRECTIVES.items():
            if sources:
                csp_parts.append(f"{directive} {' '.join(sources)}")
            else:
                csp_parts.append(directive)
        
        csp_header = '; '.join(csp_parts)
        
        # Add CSP header
        # Use Report-Only for development, enforcement in production
        if request.META.get('DEBUG'):
            response['Content-Security-Policy-Report-Only'] = csp_header
        else:
            response['Content-Security-Policy'] = csp_header
        
        return response