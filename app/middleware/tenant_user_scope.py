"""
Tenant and User Scope Middleware
Sets Sentry user context and tenant information for authenticated requests
"""

import logging
from typing import Callable, Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from ..casdoor_oidc import CasdoorUser
from ..observability.sentry import set_user_context

logger = logging.getLogger(__name__)


class TenantUserScopeMiddleware(BaseHTTPMiddleware):
    """
    Middleware that sets Sentry user context and tenant information

    Extracts user and tenant information from authenticated requests and
    sets appropriate Sentry context for tracking and debugging.
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Extract user and tenant information
        user_info = self._extract_user_info(request)
        tenant_info = self._extract_tenant_info(request)

        # Set Sentry context if user is authenticated
        if user_info:
            try:
                set_user_context(
                    user_id=user_info.get("id", "unknown"),
                    username=user_info.get("username"),
                    tenant_id=tenant_info.get("id") if tenant_info else None,
                )

                logger.debug(
                    f"Set Sentry user context",
                    extra={
                        "request_id": getattr(request.state, "request_id", "unknown"),
                        "user_id": user_info.get("id"),
                        "tenant_id": tenant_info.get("id") if tenant_info else None,
                    },
                )

            except Exception as e:
                logger.error(f"Failed to set Sentry user context: {e}")

        # Process the request
        response = await call_next(request)

        return response

    def _extract_user_info(self, request: Request) -> Optional[dict]:
        """
        Extract user information from request

        Args:
            request: FastAPI request object

        Returns:
            Dictionary with user information or None
        """
        try:
            # Check if user is already authenticated and stored in request state
            if hasattr(request.state, "user") and request.state.user:
                user = request.state.user
                if isinstance(user, CasdoorUser):
                    return {
                        "id": user.id,
                        "username": user.name,
                        "email": user.email,
                        "organization": user.organization,
                        "roles": user.roles,
                    }

            # Check if user is in dependencies (for endpoints that use Depends)
            # This is a fallback for cases where user might not be in state yet
            if hasattr(request, "scope") and "user" in request.scope:
                user = request.scope["user"]
                if user and hasattr(user, "id"):
                    return {
                        "id": getattr(user, "id", "unknown"),
                        "username": getattr(user, "name", "unknown"),
                        "email": getattr(user, "email", None),
                        "organization": getattr(user, "organization", None),
                        "roles": getattr(user, "roles", []),
                    }

            return None

        except Exception as e:
            logger.error(f"Error extracting user info: {e}")
            return None

    def _extract_tenant_info(self, request: Request) -> Optional[dict]:
        """
        Extract tenant information from request

        Args:
            request: FastAPI request object

        Returns:
            Dictionary with tenant information or None
        """
        try:
            # Check for tenant in headers
            tenant_header = request.headers.get("X-Tenant-ID") or request.headers.get(
                "X-Organization-ID"
            )
            if tenant_header:
                return {"id": tenant_header, "source": "header"}

            # Check for tenant in query parameters
            tenant_query = request.query_params.get(
                "tenant"
            ) or request.query_params.get("organization")
            if tenant_query:
                return {"id": tenant_query, "source": "query"}

            # Check for tenant in path parameters
            tenant_path = request.path_params.get("tenant") or request.path_params.get(
                "organization"
            )
            if tenant_path:
                return {"id": tenant_path, "source": "path"}

            # Try to extract from user organization if available
            user_info = self._extract_user_info(request)
            if user_info and user_info.get("organization"):
                return {"id": user_info["organization"], "source": "user"}

            return None

        except Exception as e:
            logger.error(f"Error extracting tenant info: {e}")
            return None


def set_user_context_for_request(request: Request, user: CasdoorUser) -> None:
    """
    Utility function to manually set user context for a request

    Useful when user authentication happens after middleware execution

    Args:
        request: FastAPI request object
        user: Authenticated user object
    """
    try:
        # Store user in request state for middleware access
        request.state.user = user

        # Set Sentry context
        set_user_context(
            user_id=user.id, username=user.name, tenant_id=user.organization
        )

        logger.debug(
            f"Manually set user context",
            extra={
                "request_id": getattr(request.state, "request_id", "unknown"),
                "user_id": user.id,
                "username": user.name,
                "tenant_id": user.organization,
            },
        )

    except Exception as e:
        logger.error(f"Failed to manually set user context: {e}")


def get_current_user_context(request: Request) -> Optional[dict]:
    """
    Get current user context from request

    Args:
        request: FastAPI request object

    Returns:
        Dictionary with user context or None
    """
    try:
        if hasattr(request.state, "user") and request.state.user:
            user = request.state.user
            if isinstance(user, CasdoorUser):
                return {
                    "id": user.id,
                    "username": user.name,
                    "email": user.email,
                    "organization": user.organization,
                    "roles": user.roles,
                }
        return None
    except Exception as e:
        logger.error(f"Error getting user context: {e}")
        return None


def get_current_tenant_context(request: Request) -> Optional[dict]:
    """
    Get current tenant context from request

    Args:
        request: FastAPI request object

    Returns:
        Dictionary with tenant context or None
    """
    try:
        # Check various sources for tenant information
        tenant_header = request.headers.get("X-Tenant-ID") or request.headers.get(
            "X-Organization-ID"
        )
        if tenant_header:
            return {"id": tenant_header, "source": "header"}

        tenant_query = request.query_params.get("tenant") or request.query_params.get(
            "organization"
        )
        if tenant_query:
            return {"id": tenant_query, "source": "query"}

        tenant_path = request.path_params.get("tenant") or request.path_params.get(
            "organization"
        )
        if tenant_path:
            return {"id": tenant_path, "source": "path"}

        # Try to get from user context
        user_context = get_current_user_context(request)
        if user_context and user_context.get("organization"):
            return {"id": user_context["organization"], "source": "user"}

        return None

    except Exception as e:
        logger.error(f"Error getting tenant context: {e}")
        return None
