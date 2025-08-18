"""
Sentry integration for Kong Auth Service
Provides error tracking, performance monitoring, and distributed tracing
"""

import json
import logging
import re
from typing import Any, Dict, Optional, Union
from urllib.parse import parse_qs, urlparse

import sentry_sdk
from sentry_sdk.integrations.aiohttp import AioHttpIntegration
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.httpx import HttpxIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.stdlib import StdlibIntegration

from ..config import settings

logger = logging.getLogger(__name__)


def _scrub_sensitive_headers(headers: Dict[str, str]) -> Dict[str, str]:
    """Remove or redact sensitive headers"""
    sensitive_headers = {
        "authorization",
        "cookie",
        "set-cookie",
        "x-api-key",
        "x-forwarded-for",
        "x-real-ip",
        "x-client-ip",
    }

    scrubbed = {}
    for key, value in headers.items():
        if key.lower() in sensitive_headers:
            scrubbed[key] = "[REDACTED]"
        else:
            scrubbed[key] = value

    return scrubbed


def _scrub_sensitive_body(body: str, content_type: str) -> str:
    """Remove or redact sensitive fields from request/response body"""
    if not body or content_type not in [
        "application/json",
        "application/x-www-form-urlencoded",
    ]:
        return body

    # Sensitive field patterns
    sensitive_patterns = [
        r'password["\']?\s*[:=]\s*["\']?[^"\']*["\']?',
        r'token["\']?\s*[:=]\s*["\']?[^"\']*["\']?',
        r'secret["\']?\s*[:=]\s*["\']?[^"\']*["\']?',
        r'otp["\']?\s*[:=]\s*["\']?[^"\']*["\']?',
        r'key["\']?\s*[:=]\s*["\']?[^"\']*["\']?',
        r'api_key["\']?\s*[:=]\s*["\']?[^"\']*["\']?',
        r'client_secret["\']?\s*[:=]\s*["\']?[^"\']*["\']?',
    ]

    scrubbed_body = body
    for pattern in sensitive_patterns:
        scrubbed_body = re.sub(
            pattern, r'\1: "[REDACTED]"', scrubbed_body, flags=re.IGNORECASE
        )

    # Truncate if too long
    if len(scrubbed_body) > 5000:
        scrubbed_body = scrubbed_body[:5000] + "... [TRUNCATED]"

    return scrubbed_body


def _scrub_query_params(query_string: str) -> str:
    """Remove or redact sensitive query parameters"""
    if not query_string:
        return query_string

    sensitive_params = {"password", "token", "secret", "otp", "key", "api_key"}

    try:
        parsed = parse_qs(query_string)
        scrubbed = {}

        for key, values in parsed.items():
            if key.lower() in sensitive_params:
                scrubbed[key] = ["[REDACTED]"]
            else:
                scrubbed[key] = values

        # Reconstruct query string
        return "&".join([f"{k}={v[0]}" for k, v in scrubbed.items()])
    except Exception:
        return query_string


def before_send(
    event: Dict[str, Any], hint: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Sentry event processor to scrub sensitive information before sending

    Args:
        event: The Sentry event to process
        hint: Additional context about the event

    Returns:
        Processed event or None to drop the event
    """
    try:
        # Scrub request headers
        if "request" in event and "headers" in event["request"]:
            event["request"]["headers"] = _scrub_sensitive_headers(
                event["request"]["headers"]
            )

        # Scrub request body
        if "request" in event and "data" in event["request"]:
            content_type = event["request"].get("headers", {}).get("content-type", "")
            if isinstance(event["request"]["data"], str):
                event["request"]["data"] = _scrub_sensitive_body(
                    event["request"]["data"], content_type
                )

        # Scrub query string
        if "request" in event and "query_string" in event["request"]:
            event["request"]["query_string"] = _scrub_query_params(
                event["request"]["query_string"]
            )

        # Scrub user context if PII should not be sent
        if not settings.should_send_default_pii:
            if "user" in event:
                event["user"] = {"id": event["user"].get("id", "[REDACTED]")}

            if "contexts" in event and "user" in event["contexts"]:
                event["contexts"]["user"] = {
                    "id": event["contexts"]["user"].get("id", "[REDACTED]")
                }

        # Add service context
        if "tags" not in event:
            event["tags"] = {}

        event["tags"].update(
            {
                "service": settings.SERVICE_NAME,
                "environment": settings.SENTRY_ENV,
                "release": settings.APP_RELEASE,
            }
        )

        # Add request context if available
        if "request" in event and "url" in event["request"]:
            try:
                parsed_url = urlparse(event["request"]["url"])
                event["tags"]["path"] = parsed_url.path
                event["tags"]["method"] = event["request"].get("method", "UNKNOWN")
            except Exception:
                pass

        return event

    except Exception as e:
        logger.error(f"Error in Sentry before_send: {e}")
        # Return None to drop the event if processing fails
        return None


def init_sentry() -> None:
    """Initialize Sentry SDK with proper configuration"""
    if not settings.SENTRY_ENABLED or not settings.SENTRY_DSN:
        logger.info("Sentry disabled or no DSN provided")
        return

    try:
        # Configure Sentry SDK
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            environment=settings.SENTRY_ENV,
            release=settings.APP_RELEASE,
            traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
            profiles_sample_rate=settings.SENTRY_PROFILES_SAMPLE_RATE,
            send_default_pii=settings.should_send_default_pii,
            before_send=before_send,
            # Integrations
            integrations=[
                FastApiIntegration(),
                HttpxIntegration(),
                AioHttpIntegration(),
                StdlibIntegration(),
                LoggingIntegration(level=logging.INFO, event_level=logging.ERROR),
            ],
            # Performance monitoring
            enable_tracing=True,
            enable_profiling=True,
            # Error handling
            max_breadcrumbs=100,
            attach_stacktrace=True,
            # Sampling
            sample_rate=1.0 if settings.is_development else 0.1,
            # Debug mode for development
            debug=settings.is_development,
        )

        logger.info(
            f"Sentry initialized successfully for environment: {settings.SENTRY_ENV}"
        )

        # Set global tags
        sentry_sdk.set_tag("service", settings.SERVICE_NAME)
        sentry_sdk.set_tag("environment", settings.SENTRY_ENV)
        sentry_sdk.set_tag("release", settings.APP_RELEASE)

    except Exception as e:
        logger.error(f"Failed to initialize Sentry: {e}")


def set_user_context(
    user_id: str, username: Optional[str] = None, tenant_id: Optional[str] = None
) -> None:
    """
    Set user context in Sentry for tracking user-specific events

    Args:
        user_id: Unique identifier for the user
        username: Optional username (will be redacted in production)
        tenant_id: Optional tenant identifier
    """
    if not settings.SENTRY_ENABLED:
        return

    try:
        user_data = {"id": user_id}

        # Only include username in non-production environments
        if username and settings.should_send_default_pii:
            user_data["username"] = username

        sentry_sdk.set_user(user_data)

        # Set tenant context if available
        if tenant_id:
            sentry_sdk.set_tag("tenant", tenant_id)

    except Exception as e:
        logger.error(f"Failed to set Sentry user context: {e}")


def set_request_context(request_id: str, path: str, method: str) -> None:
    """
    Set request context in Sentry for tracking request-specific events

    Args:
        request_id: Unique request identifier
        path: Request path
        method: HTTP method
    """
    if not settings.SENTRY_ENABLED:
        return

    try:
        sentry_sdk.set_tag("request_id", request_id)
        sentry_sdk.set_tag("path", path)
        sentry_sdk.set_tag("method", method)

    except Exception as e:
        logger.error(f"Failed to set Sentry request context: {e}")


def capture_exception(error: Exception, **kwargs) -> Optional[str]:
    """
    Capture an exception in Sentry with additional context

    Args:
        error: The exception to capture
        **kwargs: Additional context data

    Returns:
        Sentry event ID if successful, None otherwise
    """
    if not settings.SENTRY_ENABLED:
        return None

    try:
        # Set additional context
        for key, value in kwargs.items():
            if key == "user_id":
                sentry_sdk.set_user({"id": value})
            elif key == "tenant_id":
                sentry_sdk.set_tag("tenant", value)
            elif key == "request_id":
                sentry_sdk.set_tag("request_id", value)
            else:
                sentry_sdk.set_tag(key, value)

        # Capture the exception
        event_id = sentry_sdk.capture_exception(error)
        return event_id

    except Exception as e:
        logger.error(f"Failed to capture exception in Sentry: {e}")
        return None


def capture_message(message: str, level: str = "info", **kwargs) -> Optional[str]:
    """
    Capture a message in Sentry with additional context

    Args:
        message: The message to capture
        level: Log level (debug, info, warning, error)
        **kwargs: Additional context data

    Returns:
        Sentry event ID if successful, None otherwise
    """
    if not settings.SENTRY_ENABLED:
        return None

    try:
        # Set additional context
        for key, value in kwargs.items():
            if key == "user_id":
                sentry_sdk.set_user({"id": value})
            elif key == "tenant_id":
                sentry_sdk.set_tag("tenant", value)
            elif key == "request_id":
                sentry_sdk.set_tag("request_id", value)
            else:
                sentry_sdk.set_tag(key, value)

        # Capture the message
        event_id = sentry_sdk.capture_message(message, level=level)
        return event_id

    except Exception as e:
        logger.error(f"Failed to capture message in Sentry: {e}")
        return None
