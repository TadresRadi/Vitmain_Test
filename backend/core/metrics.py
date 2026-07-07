"""
Custom Prometheus metrics.
"""

try:
    from prometheus_client import Counter

    API_KEY_USAGE = Counter(
        "vitmain_api_key_usage_total",
        "API Key usage",
        ["key_prefix", "endpoint"],
    )

    API_ERRORS = Counter(
        "vitmain_api_errors_total",
        "Application errors",
    )

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