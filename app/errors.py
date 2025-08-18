"""
Error handling system for Kong Auth Service
Provides canonical error classes and FastAPI exception handlers with Sentry integration
"""

import logging
import traceback
from typing import Any, Dict, List, Optional, Union

import sentry_sdk
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from .config import settings
from .middleware.request_id import get_request_id_safe
from .observability.sentry import capture_exception

logger = logging.getLogger(__name__)


class AppError(Exception):
    """Base application error class"""

    def __init__(
        self,
        status_code: int = 500,
        code: str = "server_error",
        message: str = "Something went wrong on our end.",
        details: Optional[Dict[str, Any]] = None,
        reference_id: Optional[str] = None,
    ):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details or {}
        self.reference_id = reference_id
        super().__init__(message)


class ValidationAppError(AppError):
    """Validation error (400)"""

    def __init__(
        self,
        message: str = "Invalid input provided.",
        details: Optional[Dict[str, Any]] = None,
        reference_id: Optional[str] = None,
    ):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="validation_error",
            message=message,
            details=details,
            reference_id=reference_id,
        )


class AuthenticationAppError(AppError):
    """Authentication error (401)"""

    def __init__(
        self,
        message: str = "Authentication required.",
        details: Optional[Dict[str, Any]] = None,
        reference_id: Optional[str] = None,
    ):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="authentication_error",
            message=message,
            details=details,
            reference_id=reference_id,
        )


class AuthorizationAppError(AppError):
    """Authorization error (403)"""

    def __init__(
        self,
        message: str = "Access denied.",
        details: Optional[Dict[str, Any]] = None,
        reference_id: Optional[str] = None,
    ):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            code="authorization_error",
            message=message,
            details=details,
            reference_id=reference_id,
        )


class NotFoundAppError(AppError):
    """Not found error (404)"""

    def __init__(
        self,
        message: str = "Resource not found.",
        details: Optional[Dict[str, Any]] = None,
        reference_id: Optional[str] = None,
    ):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            code="not_found_error",
            message=message,
            details=details,
            reference_id=reference_id,
        )


class ConflictAppError(AppError):
    """Conflict error (409)"""

    def __init__(
        self,
        message: str = "Resource conflict.",
        details: Optional[Dict[str, Any]] = None,
        reference_id: Optional[str] = None,
    ):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            code="conflict_error",
            message=message,
            details=details,
            reference_id=reference_id,
        )


class RateLimitAppError(AppError):
    """Rate limit error (429)"""

    def __init__(
        self,
        message: str = "Rate limit exceeded.",
        details: Optional[Dict[str, Any]] = None,
        reference_id: Optional[str] = None,
    ):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            code="rate_limit_error",
            message=message,
            details=details,
            reference_id=reference_id,
        )


class ServiceUnavailableAppError(AppError):
    """Service unavailable error (503)"""

    def __init__(
        self,
        message: str = "Service temporarily unavailable.",
        details: Optional[str] = None,
        reference_id: Optional[str] = None,
    ):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            code="service_unavailable_error",
            message=message,
            details=details,
            reference_id=reference_id,
        )


def _get_reference_id(request: Request, error: Exception) -> str:
    """
    Get reference ID for error tracking

    Args:
        request: FastAPI request object
        error: The exception that occurred

    Returns:
        Reference ID string
    """
    try:
        # Try to get Sentry event ID first
        if hasattr(sentry_sdk, "last_event_id"):
            event_id = sentry_sdk.last_event_id()
            if event_id:
                return str(event_id)
    except Exception:
        pass

    # Fallback to request ID
    try:
        return get_request_id_safe(request)
    except Exception:
        pass

    # Final fallback
    return "unknown"


def _create_error_response(
    request: Request,
    error: Exception,
    status_code: int,
    code: str,
    message: str,
    details: Optional[Dict[str, Any]] = None,
) -> JSONResponse:
    """
    Create standardized error response

    Args:
        request: FastAPI request object
        error: The exception that occurred
        status_code: HTTP status code
        code: Error code string
        message: User-friendly error message
        details: Additional error details

    Returns:
        JSONResponse with error information
    """
    reference_id = _get_reference_id(request, error)

    response_data = {
        "success": False,
        "error": {"code": code, "message": message, "reference_id": reference_id},
    }

    # Add details in non-production environments
    if details and not settings.is_production:
        response_data["error"]["details"] = details

    # Log the error
    logger.error(
        f"Error occurred: {code}",
        extra={
            "request_id": get_request_id_safe(request),
            "status_code": status_code,
            "error_code": code,
            "error_message": message,
            "reference_id": reference_id,
            "details": details,
            "exception_type": type(error).__name__,
            "exception_message": str(error),
        },
    )

    return JSONResponse(status_code=status_code, content=response_data)


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """Handle AppError exceptions"""
    return _create_error_response(
        request=request,
        error=exc,
        status_code=exc.status_code,
        code=exc.code,
        message=exc.message,
        details=exc.details,
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTPException exceptions"""
    # Map common HTTP status codes to friendly messages
    friendly_messages = {
        400: "Bad request",
        401: "Authentication required",
        403: "Access denied",
        404: "Resource not found",
        405: "Method not allowed",
        409: "Resource conflict",
        422: "Validation error",
        429: "Too many requests",
        500: "Internal server error",
        502: "Bad gateway",
        503: "Service unavailable",
        504: "Gateway timeout",
    }

    message = friendly_messages.get(exc.status_code, exc.detail or "An error occurred")

    return _create_error_response(
        request=request,
        error=exc,
        status_code=exc.status_code,
        code=f"http_{exc.status_code}",
        message=message,
    )


async def validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle request validation errors"""
    # Extract field errors
    field_errors = []
    for error in exc.errors():
        field_path = " -> ".join(str(loc) for loc in error["loc"])
        field_errors.append(
            {"field": field_path, "message": error["msg"], "type": error["type"]}
        )

    # Create user-friendly message
    if len(field_errors) == 1:
        message = f"Invalid input: {field_errors[0]['message']}"
    else:
        message = f"Invalid input in {len(field_errors)} fields"

    details = {"field_errors": field_errors} if not settings.is_production else None

    return _create_error_response(
        request=request,
        error=exc,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        code="validation_error",
        message=message,
        details=details,
    )


async def pydantic_validation_error_handler(
    request: Request, exc: ValidationError
) -> JSONResponse:
    """Handle Pydantic validation errors"""
    # Extract field errors
    field_errors = []
    for error in exc.errors():
        field_path = " -> ".join(str(loc) for loc in error["loc"])
        field_errors.append(
            {"field": field_path, "message": error["msg"], "type": error["type"]}
        )

    message = f"Data validation failed: {len(field_errors)} field(s) have errors"
    details = {"field_errors": field_errors} if not settings.is_production else None

    return _create_error_response(
        request=request,
        error=exc,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        code="validation_error",
        message=message,
        details=details,
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all unhandled exceptions"""
    # Capture in Sentry
    try:
        capture_exception(
            exc,
            request_id=get_request_id_safe(request),
            path=request.url.path,
            method=request.method,
        )
    except Exception as sentry_error:
        logger.error(f"Failed to capture exception in Sentry: {sentry_error}")

    # Log the full error with traceback
    logger.error(
        f"Unhandled exception: {type(exc).__name__}",
        extra={
            "request_id": get_request_id_safe(request),
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "traceback": traceback.format_exc(),
        },
    )

    # Return safe error message
    message = "An unexpected error occurred" if settings.is_production else str(exc)

    return _create_error_response(
        request=request,
        error=exc,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code="internal_server_error",
        message=message,
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers with the FastAPI app"""

    # Register custom error handlers
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(ValidationError, pydantic_validation_error_handler)

    # Register generic handler last (catches everything else)
    app.add_exception_handler(Exception, generic_exception_handler)

    logger.info("Exception handlers registered successfully")


def raise_not_found(message: str = "Resource not found") -> None:
    """Raise a not found error"""
    raise NotFoundAppError(message=message)


def raise_validation_error(
    message: str, details: Optional[Dict[str, Any]] = None
) -> None:
    """Raise a validation error"""
    raise ValidationAppError(message=message, details=details)


def raise_authentication_error(message: str = "Authentication required") -> None:
    """Raise an authentication error"""
    raise AuthenticationAppError(message=message)


def raise_authorization_error(message: str = "Access denied") -> None:
    """Raise an authorization error"""
    raise AuthorizationAppError(message=message)


def raise_conflict_error(message: str = "Resource conflict") -> None:
    """Raise a conflict error"""
    raise ConflictAppError(message=message)


def raise_rate_limit_error(message: str = "Rate limit exceeded") -> None:
    """Raise a rate limit error"""
    raise RateLimitAppError(message=message)
