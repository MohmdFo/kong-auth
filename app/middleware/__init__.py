"""
Middleware module for Kong Auth Service
Provides request processing, authentication context, and observability middleware
"""

from .cors import get_cors_origins, is_origin_allowed, setup_cors_middleware
from .request_id import RequestIDMiddleware
from .sentry import (
    SentryMiddleware,
    capture_request_error,
    capture_request_message,
    setup_sentry_middleware,
)
from .tenant_user_scope import (
    TenantUserScopeMiddleware,
    get_current_tenant_context,
    get_current_user_context,
    set_user_context_for_request,
)

__all__ = [
    "RequestIDMiddleware",
    "TenantUserScopeMiddleware",
    "set_user_context_for_request",
    "get_current_user_context",
    "get_current_tenant_context",
    "SentryMiddleware",
    "setup_sentry_middleware",
    "capture_request_error",
    "capture_request_message",
    "setup_cors_middleware",
    "get_cors_origins",
    "is_origin_allowed",
]
