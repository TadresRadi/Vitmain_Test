import logging
import time
from django.conf import settings
from django.db import connection

logger = logging.getLogger('django.db.backends')

class QueryTimingMiddleware:
    """
    Middleware to log slow requests/queries (development/production toggle).
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.time()
        response = self.get_response(request)
        duration_ms = (time.time() - start) * 1000

        if duration_ms > getattr(settings, "SLOW_QUERY_THRESHOLD_MS", 200):
            # Log summary and last few DB queries
            queries = connection.queries[-5:] if hasattr(connection, "queries") else []
            logger.warning(
                "Slow request: %s ms path=%s method=%s queries=%d last_queries=%s",
                int(duration_ms),
                request.path,
                request.method,
                len(connection.queries) if hasattr(connection, "queries") else 0,
                queries,
            )
        return response