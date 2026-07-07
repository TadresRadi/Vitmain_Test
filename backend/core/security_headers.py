from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

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

        # Copy directives so we can mutate per-request
        directives = {k: list(v) for k, v in self.CSP_DIRECTIVES.items()}

        # If in DEBUG (development), allow the backend origin (where media is served)
        # so frontend (served on a different origin) can load media from this backend.
        if settings.DEBUG:
            try:
                backend_origin = f"{request.scheme}://{request.get_host()}"
                if backend_origin not in directives['img-src']:
                    directives['img-src'].append(backend_origin)
            except Exception:
                # If anything goes wrong, do not break response generation
                pass

        # Build CSP header value
        csp_parts = []
        for directive, sources in directives.items():
            if sources:
                csp_parts.append(f"{directive} {' '.join(sources)}")
            else:
                csp_parts.append(directive)

        csp_header = '; '.join(csp_parts)

        # Use Report-Only in DEBUG so you can iterate safely; enforce in production.
        if settings.DEBUG:
            response['Content-Security-Policy-Report-Only'] = csp_header
        else:
            response['Content-Security-Policy'] = csp_header

        return response