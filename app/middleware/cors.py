"""
CORS middleware configuration for Kong Auth Service
Handles Cross-Origin Resource Sharing for frontend integration
"""

import logging
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ..config import settings

logger = logging.getLogger(__name__)


def setup_cors_middleware(app: FastAPI) -> None:
    """
    Configure CORS middleware for the FastAPI application.
    
    This enables frontend applications to make requests to the API
    by configuring appropriate CORS headers.
    
    Args:
        app: FastAPI application instance
    """
    logger.info("Setting up CORS middleware")
    logger.info(f"CORS Origins: {settings.CORS_ORIGINS}")
    logger.info(f"CORS Allow Credentials: {settings.CORS_ALLOW_CREDENTIALS}")
    logger.info(f"CORS Allow Methods: {settings.CORS_ALLOW_METHODS}")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
    )
    
    logger.info("✅ CORS middleware configured successfully")


def get_cors_origins() -> List[str]:
    """
    Get the list of allowed CORS origins.
    
    Returns:
        List of allowed origin URLs
    """
    return settings.CORS_ORIGINS


def is_origin_allowed(origin: str) -> bool:
    """
    Check if a given origin is allowed by CORS configuration.
    
    Args:
        origin: The origin URL to check
        
    Returns:
        True if origin is allowed, False otherwise
    """
    if "*" in settings.CORS_ORIGINS:
        return True
    
    return origin in settings.CORS_ORIGINS