"""
Authentication and user-related views.
"""
import logging

from fastapi import APIRouter, Depends

from ..casdoor_oidc import CasdoorUser, get_current_user
from ..metrics.base import CASDOOR_AUTH_SUCCESS_COUNT

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/")
async def root():
    """Root endpoint."""
    logger.info("Root endpoint accessed")
    return {"message": "Kong Auth Service is running"}


@router.get("/me")
async def get_current_user_info(current_user: CasdoorUser = Depends(get_current_user)):
    """Get information about the currently authenticated user."""
    logger.info(f"User info requested for: {current_user.name}")

    # Track successful Casdoor authentication
    CASDOOR_AUTH_SUCCESS_COUNT.labels(username=current_user.name).inc()

    return {
        "id": current_user.id,
        "name": current_user.name,
        "display_name": current_user.display_name,
        "email": current_user.email,
        "phone": current_user.phone,
        "avatar": current_user.avatar,
        "organization": current_user.organization,
        "roles": current_user.roles,
        "permissions": current_user.permissions,
    }
