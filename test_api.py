#!/usr/bin/env python3
"""
Test script for the Kong Auth Service API
"""

import asyncio
import httpx
import json

BASE_URL = "http://localhost:8000"

async def test_api():
    async with httpx.AsyncClient() as client:
        print("Testing Kong Auth Service API...")

        # Test root endpoint
        print("\n1. Testing root endpoint...")
        try:
            response = await client.get(f"{BASE_URL}/")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
        except Exception as e:
            print(f"Error: {e}")

        # Test creating a consumer
        print("\n2. Testing consumer creation...")
        consumer_data = {
            "username": "testuser123",
            "custom_id": "test-custom-id"
        }

        try:
            response = await client.post(
                f"{BASE_URL}/create-consumer",
                json=consumer_data
            )
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"Consumer ID: {result['consumer_id']}")
                print(f"Token: {result['token'][:50]}...")
                print(f"Expires at: {result['expires_at']}")
                print(f"Secret: {result['secret'][:20]}...")

                # Store consumer ID for later tests
                consumer_id = result['consumer_id']
            else:
                print(f"Error: {response.text}")
                return
        except Exception as e:
            print(f"Error: {e}")
            return

        # Test listing consumers
        print("\n3. Testing list consumers...")
        try:
            response = await client.get(f"{BASE_URL}/consumers")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                consumers = response.json()
                print(f"Found {len(consumers)} consumers")
                for consumer in consumers:
                    print(f"  - {consumer.get('username', 'N/A')} (ID: {consumer.get('id', 'N/A')})")
            else:
                print(f"Error: {response.text}")
        except Exception as e:
            print(f"Error: {e}")

        # Test getting specific consumer
        print(f"\n4. Testing get consumer {consumer_id}...")
        try:
            response = await client.get(f"{BASE_URL}/consumers/{consumer_id}")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                consumer = response.json()
                print(f"Consumer: {consumer}")
            else:
                print(f"Error: {response.text}")
        except Exception as e:
            print(f"Error: {e}")

        # Test creating the same consumer again (should return existing)
        print("\n5. Testing duplicate consumer creation...")
        try:
            response = await client.post(
                f"{BASE_URL}/create-consumer",
                json=consumer_data
            )
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"Consumer ID: {result['consumer_id']}")
                print("Successfully handled duplicate consumer")
            else:
                print(f"Error: {response.text}")
        except Exception as e:
            print(f"Error: {e}")

        print("\nAPI testing completed!")

if __name__ == "__main__":
    asyncio.run(test_api()) 