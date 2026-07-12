"""
Prometheus metrics middleware.

Records HTTP request duration (latency) for every request, labeled by
HTTP method, endpoint path, and response status code.

The metric is exposed at /metrics (when ENABLE_PROMETHEUS=true) and
scraped by Prometheus. This enables p50/p95/p99 latency alerts.
"""
import time

from core.metrics import observe_request_duration


class PrometheusMetricsMiddleware:
    """
    Records request duration for every HTTP request.

    Placed AFTER RequestIDMiddleware so request.id is available,
    and AFTER PrometheusAfterMiddleware so the response status is final.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.perf_counter()

        try:
            response = self.get_response(request)
            duration = time.perf_counter() - start

            # Use the resolved path_info to group similar endpoints
            # (e.g. /api/users/123/ -> /api/users/{id}/ would be ideal
            # but path_info is the simplest stable identifier we have).
            endpoint = request.path_info or "/"

            observe_request_duration(
                method=request.method,
                endpoint=endpoint,
                status_code=response.status_code,
                duration_seconds=duration,
            )

            return response

        except Exception:
            # Re-raise the exception — Django's exception handler will
            # convert it to a 500. We still record the latency with a 500
            # status so the alert rules can catch error latency spikes.
            duration = time.perf_counter() - start
            observe_request_duration(
                method=request.method,
                endpoint=request.path_info or "/",
                status_code=500,
                duration_seconds=duration,
            )
            raise