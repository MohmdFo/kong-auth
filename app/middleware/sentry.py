"""
Sentry middleware for FastAPI
Provides request context, user tracking, and error capture
"""

import time
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from ..observability.sentry import (
    init_sentry,
    set_user_context,
    set_request_context,
    capture_exception,
    capture_message
)
from ..config import settings

logger = logging.getLogger(__name__)


class SentryMiddleware(BaseHTTPMiddleware):
    """Middleware to integrate Sentry with FastAPI requests"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        # Initialize Sentry if not already done
        init_sentry()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and capture Sentry context"""
        start_time = time.time()
        
        try:
            # Set request context in Sentry
            request_id = getattr(request.state, 'request_id', 'unknown') if hasattr(request, 'state') else 'unknown'
            set_request_context(request_id, request.url.path, request.method)
            
            # Process the request
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Log successful request if it's slow (>1 second)
            if duration > 1.0:
                capture_message(
                    f"Slow request: {request.method} {request.url.path} took {duration:.2f}s",
                    level="warning",
                    request_id=request_id,
                    duration=duration
                )
            
            return response
            
        except Exception as e:
            # Calculate duration before handling error
            duration = time.time() - start_time
            
            # Capture exception in Sentry
            request_id = getattr(request.state, 'request_id', 'unknown') if hasattr(request, 'state') else 'unknown'
            
            # Set user context if available
            if hasattr(request, 'state') and hasattr(request.state, 'user') and request.state.user:
                user = request.state.user
                user_id = getattr(user, 'id', None)
                username = getattr(user, 'name', None)
                tenant_id = getattr(user, 'organization', None)
                
                if user_id:
                    set_user_context(user_id, username, tenant_id)
            
            # Capture the exception with context
            capture_exception(
                e,
                request_id=request_id,
                path=request.url.path,
                method=request.method,
                duration=duration,
                user_agent=request.headers.get("user-agent", ""),
                client_ip=request.client.host if request.client else "unknown"
            )
            
            # Re-raise the exception
            raise


def setup_sentry_middleware(app):
    """Setup Sentry middleware for the FastAPI app"""
    if settings.SENTRY_ENABLED:
        app.add_middleware(SentryMiddleware)
        logger.info("Sentry middleware added to FastAPI app")
    else:
        logger.info("Sentry middleware not added (Sentry disabled)")


def capture_request_error(error: Exception, request: Request, **kwargs):
    """Capture a request error in Sentry with full context"""
    if not settings.SENTRY_ENABLED:
        return None
    
    try:
        # Extract request context
        request_id = getattr(request.state, 'request_id', 'unknown') if hasattr(request, 'state') else 'unknown'
        client_ip = request.client.host if request.client else "unknown"
        
        # Extract user context if available
        user_context = {}
        if hasattr(request, 'state') and hasattr(request.state, 'user') and request.state.user:
            user = request.state.user
            user_context.update({
                'user_id': getattr(user, 'id', None),
                'username': getattr(user, 'name', None),
                'tenant_id': getattr(user, 'organization', None)
            })
        
        # Capture the exception
        return capture_exception(
            error,
            request_id=request_id,
            path=request.url.path,
            method=request.method,
            client_ip=client_ip,
            user_agent=request.headers.get("user-agent", ""),
            **user_context,
            **kwargs
        )
        
    except Exception as e:
        logger.error(f"Failed to capture request error in Sentry: {e}")
        return None


def capture_request_message(message: str, level: str = "info", request: Request = None, **kwargs):
    """Capture a request message in Sentry with context"""
    if not settings.SENTRY_ENABLED:
        return None
    
    try:
        if request:
            # Extract request context
            request_id = getattr(request.state, 'request_id', 'unknown') if hasattr(request, 'state') else 'unknown'
            client_ip = request.client.host if request.client else "unknown"
            
            # Extract user context if available
            user_context = {}
            if hasattr(request, 'state') and hasattr(request.state, 'user') and request.state.user:
                user = request.state.user
                user_context.update({
                    'user_id': getattr(user, 'id', None),
                    'username': getattr(user, 'name', None),
                    'tenant_id': getattr(user, 'organization', None)
                })
            
            kwargs.update({
                'request_id': request_id,
                'path': request.url.path,
                'method': request.method,
                'client_ip': client_ip,
                'user_agent': request.headers.get("user-agent", ""),
                **user_context
            })
        
        # Capture the message
        return capture_message(message, level=level, **kwargs)
        
    except Exception as e:
        logger.error(f"Failed to capture request message in Sentry: {e}")
        return None
