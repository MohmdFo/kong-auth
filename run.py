#!/usr/bin/env python3
"""
Run script for the Kong Auth Service
"""

import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

if __name__ == "__main__":
    # Get configuration from environment variables
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "true").lower() == "true"

    print(f"Starting Kong Auth Service on {host}:{port}")
    print(f"Kong Admin URL: {os.getenv('KONG_ADMIN_URL', 'http://localhost:8006')}")
    print(f"JWT Expiration: {os.getenv('JWT_EXPIRATION_SECONDS', '31536000')} seconds")

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
