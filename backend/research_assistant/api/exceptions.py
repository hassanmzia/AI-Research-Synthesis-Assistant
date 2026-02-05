"""Custom exception handler for the REST API."""
import logging

from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        response.data["status_code"] = response.status_code

        # Add request ID for debugging
        request = context.get("request")
        if request:
            response.data["request_id"] = getattr(request, "request_id", None)

    else:
        logger.exception(f"Unhandled exception: {exc}")

    return response
