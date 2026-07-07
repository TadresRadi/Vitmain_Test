"""
Middleware to detect slow requests and log last DB queries.
Toggle via SLOW_QUERY_THRESHOLD_MS (ms) in environment / settings.
"""
import logging
import time
from django.conf import settings
from django.db import connection

logger = logging.getLogger("django.db.backends")

class QueryTimingMiddleware:
    """
    Logs requests that exceed SLOW_QUERY_THRESHOLD_MS (default 200ms).
    Writes a warning with the path, method, duration and last few DB queries.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.threshold_ms = int(getattr(settings, "SLOW_QUERY_THRESHOLD_MS", 200))

    def __call__(self, request):
        start = time.perf_counter()
        response = self.get_response(request)
        duration_ms = (time.perf_counter() - start) * 1000

        try:
            # Only log when threshold exceeded
            if duration_ms > self.threshold_ms:
                # capture last N queries (if DEBUG/connection collects them)
                queries = getattr(connection, "queries", [])
                if queries:
                    last_queries = queries[-10:]
                else:
                    last_queries = []
                logger.warning(
                    "Slow request: duration_ms=%d path=%s method=%s queries=%d last_queries=%s",
                    int(duration_ms),
                    request.path,
                    request.method,
                    len(getattr(connection, "queries", [])),
                    last_queries,
                )
        except Exception:
            logger.exception("Error in QueryTimingMiddleware")

        return response