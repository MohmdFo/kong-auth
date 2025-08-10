"""
Middleware module for Kong Auth Service
Provides request processing, authentication context, and observability middleware
"""

from .request_id import RequestIDMiddleware
from .tenant_user_scope import (
    TenantUserScopeMiddleware,
    set_user_context_for_request,
    get_current_user_context,
    get_current_tenant_context
)
from .sentry import (
    SentryMiddleware,
    setup_sentry_middleware,
    capture_request_error,
    capture_request_message
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
    "capture_request_message"
]
