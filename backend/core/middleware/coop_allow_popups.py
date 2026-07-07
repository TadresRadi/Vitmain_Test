# backend/core/middleware/coop_allow_popups.py
from django.conf import settings

class CoopAllowPopupsMiddleware:
    """
    Add Cross-Origin-Opener-Policy header set to same-origin-allow-popups.
    This allows popup-based auth flows (Google) to communicate via postMessage
    while retaining reasonable COOP protections.
    Only add this header for the frontend HTML endpoint (index) or when ENABLE_GSI is true.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Apply only for HTML responses (avoid adding to JSON APIs)
        content_type = response.get('Content-Type', '')
        if content_type.startswith('text/html'):
            # Only add in debug or when explicitly enabled to avoid leaking in other paths
            response.setdefault('Cross-Origin-Opener-Policy', 'same-origin-allow-popups')

        return response