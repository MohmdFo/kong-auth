#!/usr/bin/env python3
"""
Run script for the Kong Auth Service
"""

import uvicorn
import os
import logging
from dotenv import load_dotenv
from app.logging_config import setup_logging
from app.observability.sentry import init_sentry

# Load environment variables from .env file if it exists
load_dotenv()

# Setup logging
setup_logging()

# Initialize Sentry
init_sentry()

# Get logger
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # Get configuration from environment variables
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "true").lower() == "true"

    logger.info(f"Starting Kong Auth Service on {host}:{port}")
    logger.info(f"Kong Admin URL: {os.getenv('KONG_ADMIN_URL', 'http://localhost:8006')}")
    logger.info(f"JWT Expiration: {os.getenv('JWT_EXPIRATION_SECONDS', '31536000')} seconds")

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
