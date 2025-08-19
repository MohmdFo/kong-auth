"""
Kong Auth Service - Main application module.

This module sets up the FastAPI application and includes all routers.
"""
import logging

from dotenv import load_dotenv
from fastapi import FastAPI

# Load environment variables from .env file
load_dotenv()

# Import routers
from .kong_api import router as kong_router
from .metrics import metrics_router
from .observability.sentry import init_sentry
from .views import auth_router, consumer_router, token_router

# Add metrics middleware
from .metrics.middleware import metrics_middleware

# Add Sentry middleware
from .middleware.sentry import setup_sentry_middleware

# Setup logging
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Kong Auth Service",
    description="Service to create Kong consumers, generate JWT tokens, and manage Kong services and routes",
    version="2.0.0",
)

# Initialize Sentry
init_sentry()

# Include routers
app.include_router(auth_router, tags=["authentication"])
app.include_router(consumer_router, tags=["consumers"])
app.include_router(token_router, tags=["tokens"])
app.include_router(kong_router)  # Already has its own tags
app.include_router(metrics_router, prefix="/metrics", tags=["metrics"])

# Add middleware
app.middleware("http")(metrics_middleware)
setup_sentry_middleware(app)
