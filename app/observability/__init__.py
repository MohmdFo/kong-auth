"""
Observability module for Kong Auth Service
Provides Sentry integration, error tracking, and performance monitoring
"""

from .sentry import (
    capture_exception,
    init_sentry,
    set_request_context,
    set_user_context,
)

__all__ = [
    "init_sentry",
    "capture_exception",
    "set_request_context",
    "set_user_context",
]
