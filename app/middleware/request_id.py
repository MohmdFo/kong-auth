"""
Request ID Middleware
Adds unique request ID to each request and propagates it through the system
"""

import logging
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from ..observability.sentry import set_request_context

logger = logging.getLogger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware that adds a unique request ID to each request

    Sets request.state.request_id and adds X-Request-ID header to responses.
    Also sets Sentry context for request tracking.
    """

    def __init__(self, app: ASGIApp, header_name: str = "X-Request-ID"):
        super().__init__(app)
        self.header_name = header_name

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate or extract request ID
        request_id = self._get_request_id(request)

        # Store in request state
        request.state.request_id = request_id

        # Set Sentry context
        set_request_context(
            request_id=request_id, path=request.url.path, method=request.method
        )

        # Process the request
        response = await call_next(request)

        # Add request ID to response headers
        response.headers[self.header_name] = request_id

        # Log request with ID
        logger.info(
            f"Request processed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "client_ip": self._get_client_ip(request),
            },
        )

        return response

    def _get_request_id(self, request: Request) -> str:
        """
        Get request ID from header or generate new one

        Args:
            request: FastAPI request object

        Returns:
            Request ID string
        """
        # Check if request ID is already provided in headers
        existing_id = request.headers.get(self.header_name)

        if existing_id:
            # Validate UUID format
            try:
                uuid.UUID(existing_id)
                return existing_id
            except ValueError:
                logger.warning(f"Invalid request ID format in header: {existing_id}")

        # Generate new UUID
        return str(uuid.uuid4())

    def _get_client_ip(self, request: Request) -> str:
        """
        Extract client IP address from request

        Args:
            request: FastAPI request object

        Returns:
            Client IP address string
        """
        # Check various headers for client IP
        headers_to_check = [
            "X-Forwarded-For",
            "X-Real-IP",
            "X-Client-IP",
            "CF-Connecting-IP",  # Cloudflare
            "True-Client-IP",  # Akamai
        ]

        for header in headers_to_check:
            if header in request.headers:
                ip = request.headers[header].split(",")[0].strip()
                if ip and ip != "unknown":
                    return ip

        # Fallback to direct connection
        if request.client:
            return request.client.host

        return "unknown"


def get_request_id(request: Request) -> str:
    """
    Utility function to get request ID from request state

    Args:
        request: FastAPI request object

    Returns:
        Request ID string

    Raises:
        AttributeError: If request ID is not set
    """
    if not hasattr(request.state, "request_id"):
        raise AttributeError(
            "Request ID not set. Ensure RequestIDMiddleware is configured."
        )

    return request.state.request_id


def get_request_id_safe(request: Request) -> str:
    """
    Safe utility function to get request ID from request state

    Args:
        request: FastAPI request object

    Returns:
        Request ID string or "unknown" if not set
    """
    try:
        return get_request_id(request)
    except AttributeError:
        return "unknown"
