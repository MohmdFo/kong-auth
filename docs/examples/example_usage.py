#!/usr/bin/env python3
"""
Example usage of the Kong Auth Service
This script demonstrates how to create a consumer, get a JWT token,
and use it to access a Kong-protected service.
"""

import asyncio
import httpx
import json
import logging
from app.logging_config import setup_logging

# Setup logging
logger = setup_logging()

# Configuration
AUTH_SERVICE_URL = "http://localhost:8000"
KONG_GATEWAY_URL = "http://localhost:8000"  # Replace with your Kong gateway URL
PROTECTED_SERVICE_PATH = "/your-service"  # Replace with your protected service path

async def main():
    logger.info("Kong Auth Service Example Usage")
    logger.info("=" * 40)

    async with httpx.AsyncClient() as client:
        # Step 1: Create a consumer and get JWT token
        logger.info("1. Creating consumer and generating JWT token...")

        consumer_data = {
            "username": "example_user",
            "custom_id": "example_custom_id"
        }

        try:
            response = await client.post(
                f"{AUTH_SERVICE_URL}/create-consumer",
                json=consumer_data
            )
            response.raise_for_status()
            result = response.json()

            logger.info(f"✅ Consumer created successfully!")
            logger.info(f"   Consumer ID: {result['consumer_id']}")
            logger.info(f"   Username: {consumer_data['username']}")
            logger.info(f"   Token expires: {result['expires_at']}")

            jwt_token = result['token']
            logger.info(f"   JWT Token: {jwt_token[:50]}...")

        except httpx.HTTPStatusError as e:
            logger.error(f"❌ Failed to create consumer: {e.response.text}")
            return
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            return

        # Step 2: Use the JWT token to access a protected service
        logger.info(f"2. Using JWT token to access protected service...")
        logger.info(f"   Gateway URL: {KONG_GATEWAY_URL}")
        logger.info(f"   Service Path: {PROTECTED_SERVICE_PATH}")

        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/json"
        }

        try:
            # This is an example request to a Kong-protected service
            # Replace the URL with your actual Kong gateway and service endpoint
            response = await client.get(
                f"{KONG_GATEWAY_URL}{PROTECTED_SERVICE_PATH}",
                headers=headers
            )

            logger.info(f"   Status Code: {response.status_code}")

            if response.status_code == 200:
                logger.info("✅ Successfully accessed protected service!")
                logger.info(f"   Response: {response.text[:200]}...")
            elif response.status_code == 401:
                logger.error("❌ Unauthorized - JWT token validation failed")
                logger.error("   Make sure your Kong JWT plugin is properly configured")
            elif response.status_code == 404:
                logger.error("❌ Service not found")
                logger.error("   Make sure the service path is correct and the service is registered in Kong")
            else:
                logger.error(f"❌ Unexpected response: {response.text}")

        except httpx.ConnectError:
            logger.error("❌ Connection error - Make sure Kong gateway is running")
        except Exception as e:
            logger.error(f"❌ Error accessing protected service: {e}")

        # Step 3: List all consumers
        logger.info(f"3. Listing all consumers...")

        try:
            response = await client.get(f"{AUTH_SERVICE_URL}/consumers")
            response.raise_for_status()
            consumers = response.json()

            logger.info(f"✅ Found {len(consumers)} consumers:")
            for consumer in consumers:
                logger.info(f"   - {consumer.get('username', 'N/A')} (ID: {consumer.get('id', 'N/A')})")

        except Exception as e:
            logger.error(f"❌ Error listing consumers: {e}")

        logger.info(f"Example completed!")
        logger.info(f"To manually test with curl:")
        logger.info(f"curl -H 'Authorization: Bearer {jwt_token}' {KONG_GATEWAY_URL}{PROTECTED_SERVICE_PATH}")

if __name__ == "__main__":
    asyncio.run(main())