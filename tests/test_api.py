#!/usr/bin/env python3
"""
Test script for the Kong Auth Service API
"""

import asyncio
import json
import logging

import httpx

from app.logging_config import setup_logging

# Setup logging
logger = setup_logging()

BASE_URL = "http://localhost:8000"


async def test_api():
    async with httpx.AsyncClient() as client:
        logger.info("Testing Kong Auth Service API...")

        # Test root endpoint
        logger.info("1. Testing root endpoint...")
        try:
            response = await client.get(f"{BASE_URL}/")
            logger.info(f"Status: {response.status_code}")
            logger.info(f"Response: {response.json()}")
        except Exception as e:
            logger.error(f"Error: {e}")

        # Test creating a consumer
        logger.info("2. Testing consumer creation...")
        consumer_data = {"username": "testuser123", "custom_id": "test-custom-id"}

        try:
            response = await client.post(
                f"{BASE_URL}/create-consumer", json=consumer_data
            )
            logger.info(f"Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Consumer ID: {result['consumer_id']}")
                logger.info(f"Token: {result['token'][:50]}...")
                logger.info(f"Expires at: {result['expires_at']}")
                logger.info(f"Secret: {result['secret'][:20]}...")

                # Store consumer ID for later tests
                consumer_id = result["consumer_id"]
            else:
                logger.error(f"Error: {response.text}")
                return
        except Exception as e:
            logger.error(f"Error: {e}")
            return

        # Test listing consumers
        logger.info("3. Testing list consumers...")
        try:
            response = await client.get(f"{BASE_URL}/consumers")
            logger.info(f"Status: {response.status_code}")
            if response.status_code == 200:
                consumers = response.json()
                logger.info(f"Found {len(consumers)} consumers")
                for consumer in consumers:
                    logger.info(
                        f"  - {consumer.get('username', 'N/A')} (ID: {consumer.get('id', 'N/A')})"
                    )
            else:
                logger.error(f"Error: {response.text}")
        except Exception as e:
            logger.error(f"Error: {e}")

        # Test getting specific consumer
        logger.info(f"4. Testing get consumer {consumer_id}...")
        try:
            response = await client.get(f"{BASE_URL}/consumers/{consumer_id}")
            logger.info(f"Status: {response.status_code}")
            if response.status_code == 200:
                consumer = response.json()
                logger.info(f"Consumer: {consumer}")
            else:
                logger.error(f"Error: {response.text}")
        except Exception as e:
            logger.error(f"Error: {e}")

        # Test creating the same consumer again (should return existing)
        logger.info("5. Testing duplicate consumer creation...")
        try:
            response = await client.post(
                f"{BASE_URL}/create-consumer", json=consumer_data
            )
            logger.info(f"Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Consumer ID: {result['consumer_id']}")
                logger.info("Successfully handled duplicate consumer")
            else:
                logger.error(f"Error: {response.text}")
        except Exception as e:
            logger.error(f"Error: {e}")

        logger.info("API testing completed!")


if __name__ == "__main__":
    asyncio.run(test_api())
