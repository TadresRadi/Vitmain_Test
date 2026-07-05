import logging
import time

from django.conf import settings

logger = logging.getLogger("django.db.backends")


class QueryTimingMiddleware:
    """
    Logs slow requests based on execution time.
    """

    def __init__(self, get_response):
        self.get_response = get_response

        self.threshold_ms = int(
            getattr(settings, "SLOW_QUERY_THRESHOLD_MS", 500)
        )

    def __call__(self, request):
        start = time.perf_counter()

        response = self.get_response(request)

        duration_ms = (time.perf_counter() - start) * 1000

        if duration_ms > self.threshold_ms:
            logger.warning(
                "Slow request %.2f ms %s %s",
                duration_ms,
                request.method,
                request.path,
            )

        return response