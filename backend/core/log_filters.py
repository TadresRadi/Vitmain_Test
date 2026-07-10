"""
Logging filters that add contextual information to log records.

These filters are used in the LOGGING config to add request IDs,
user IDs, and other context to every log line.
"""
import logging


class RequestIDFilter(logging.Filter):
    """
    Logging filter that adds the current request ID to every log record.

    The request ID is set on the log record as `request_id`. If no
    request is active (e.g., in a management command or Celery task),
    the value is '-'.

    Usage in LOGGING config:
        'formatters': {
            'verbose': {
                'format': '{levelname} {asctime} [req:{request_id}] {module} {message}',
                'style': '{',
            },
        },
        'filters': {
            'request_id': {
                '()': 'core.log_filters.RequestIDFilter',
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'verbose',
                'filters': ['request_id'],
            },
        },
    """

    def filter(self, record):
        # Try to get the request ID from thread-local storage.
        # The middleware sets this via _set_current_request_id().
        request_id = _get_current_request_id()
        record.request_id = request_id or "-"
        return True


# ============================================================================
# Thread-local request ID storage
# ============================================================================

import threading

_thread_local = threading.local()


def _set_current_request_id(request_id: str):
    """Set the request ID for the current thread."""
    _thread_local.request_id = request_id


def _get_current_request_id() -> str:
    """Get the request ID for the current thread, or None."""
    return getattr(_thread_local, "request_id", None)


def _clear_current_request_id():
    """Clear the request ID for the current thread."""
    if hasattr(_thread_local, "request_id"):
        del _thread_local.request_id