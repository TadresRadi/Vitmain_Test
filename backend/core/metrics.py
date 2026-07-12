"""
Custom Prometheus metrics.
"""

try:
    from prometheus_client import Counter, Histogram

    API_KEY_USAGE = Counter(
        "vitmain_api_key_usage_total",
        "API Key usage",
        ["key_prefix", "endpoint"],
    )

    API_ERRORS = Counter(
        "vitmain_api_errors_total",
        "Application errors",
    )

    # Request duration histogram — enables p50/p95/p99 latency alerts.
    # Buckets chosen for HTTP API latency (in seconds):
    #   5ms, 10ms, 25ms, 50ms, 100ms, 250ms, 500ms, 1s, 2.5s, 5s, 10s
    REQUEST_DURATION = Histogram(
        "vitmain_request_duration_seconds",
        "HTTP request duration in seconds",
        ["method", "endpoint", "status_code"],
        buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
    )

except Exception:
    API_KEY_USAGE = None
    API_ERRORS = None
    REQUEST_DURATION = None

except Exception:
    API_KEY_USAGE = None
    API_ERRORS = None


def inc_api_key_usage(prefix, endpoint):
    if API_KEY_USAGE:
        API_KEY_USAGE.labels(
            key_prefix=prefix,
            endpoint=endpoint,
        ).inc()


def inc_app_error():
    if API_ERRORS:
        API_ERRORS.inc()

def observe_request_duration(method, endpoint, status_code, duration_seconds):
    if REQUEST_DURATION:
        REQUEST_DURATION.labels(
            method=method,
            endpoint=endpoint,
            status_code=str(status_code),
        ).observe(duration_seconds)