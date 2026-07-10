"""
Request ID middleware.

Generates a unique ID for each request and attaches it to:
1. The request object (request.id)
2. The response header (X-Request-ID)
3. A thread-local variable (for the logging filter)

This makes it possible to trace a single request through all log lines.
"""
import uuid

from django.http import HttpRequest, HttpResponse

from core.log_filters import _set_current_request_id, _clear_current_request_id


class RequestIDMiddleware:
    """
    Middleware that generates a unique request ID for each request.

    The ID is:
    - Read from the X-Request-ID header if provided by the client
      (useful for distributed tracing through an API gateway).
    - Otherwise generated as a UUID.
    - Stored on request.id for use in views/services.
    - Stored in thread-local storage for the logging filter.
    - Returned in the X-Request-ID response header.
    """

    HEADER_NAME = "X-Request-ID"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # Check if the client provided a request ID (e.g., from an API gateway)
        request_id = request.headers.get(self.HEADER_NAME, "").strip()

        # Generate a new ID if none provided or if it's too long/short
        if not request_id or len(request_id) > 64:
            request_id = uuid.uuid4().hex[:12]

        # Attach to the request for use in views/services
        request.id = request_id

        # Store in thread-local so the logging filter can access it
        _set_current_request_id(request_id)

        try:
            # Process the response
            response = self.get_response(request)

            # Add the request ID to the response header
            response[self.HEADER_NAME] = request_id

            return response
        finally:
            # Always clear the thread-local, even if an exception occurs
            _clear_current_request_id()