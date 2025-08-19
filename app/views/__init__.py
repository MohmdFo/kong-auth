"""
Views package initialization.
"""
from .auth_views import router as auth_router
from .consumer_views import router as consumer_router
from .token_views import router as token_router

__all__ = [
    "auth_router",
    "consumer_router",
    "token_router",
]
