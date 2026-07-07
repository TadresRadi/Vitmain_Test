from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

class NoCacheMediaMiddleware(MiddlewareMixin):
    """
    Development helper: prevent aggressive browser caching for media files.
    Adds no-cache headers for requests whose path starts with MEDIA_URL.
    Enable only in DEBUG.
    """
    def process_response(self, request, response):
        try:
            media_url = settings.MEDIA_URL or '/media/'
            if request.path.startswith(media_url) and settings.DEBUG:
                response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
                response['Pragma'] = 'no-cache'
                response['Expires'] = '0'
        except Exception:
            # Never raise from middleware in production flow
            pass
        return response