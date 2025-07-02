#!/usr/bin/env python3
"""
Example usage of the Kong Auth Service
This script demonstrates how to create a consumer, get a JWT token,
and use it to access a Kong-protected service.
"""

import asyncio
import httpx
import json

# Configuration
AUTH_SERVICE_URL = "http://localhost:8000"
KONG_GATEWAY_URL = "http://localhost:8000"  # Replace with your Kong gateway URL
PROTECTED_SERVICE_PATH = "/your-service"  # Replace with your protected service path

async def main():
    print("Kong Auth Service Example Usage")
    print("=" * 40)

    async with httpx.AsyncClient() as client:
        # Step 1: Create a consumer and get JWT token
        print("\n1. Creating consumer and generating JWT token...")

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

            print(f"✅ Consumer created successfully!")
            print(f"   Consumer ID: {result['consumer_id']}")
            print(f"   Username: {consumer_data['username']}")
            print(f"   Token expires: {result['expires_at']}")

            jwt_token = result['token']
            print(f"   JWT Token: {jwt_token[:50]}...")

        except httpx.HTTPStatusError as e:
            print(f"❌ Failed to create consumer: {e.response.text}")
            return
        except Exception as e:
            print(f"❌ Error: {e}")
            return

        # Step 2: Use the JWT token to access a protected service
        print(f"\n2. Using JWT token to access protected service...")
        print(f"   Gateway URL: {KONG_GATEWAY_URL}")
        print(f"   Service Path: {PROTECTED_SERVICE_PATH}")

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

            print(f"   Status Code: {response.status_code}")

            if response.status_code == 200:
                print("✅ Successfully accessed protected service!")
                print(f"   Response: {response.text[:200]}...")
            elif response.status_code == 401:
                print("❌ Unauthorized - JWT token validation failed")
                print("   Make sure your Kong JWT plugin is properly configured")
            elif response.status_code == 404:
                print("❌ Service not found")
                print("   Make sure the service path is correct and the service is registered in Kong")
            else:
                print(f"❌ Unexpected response: {response.text}")

        except httpx.ConnectError:
            print("❌ Connection error - Make sure Kong gateway is running")
        except Exception as e:
            print(f"❌ Error accessing protected service: {e}")

        # Step 3: List all consumers
        print(f"\n3. Listing all consumers...")

        try:
            response = await client.get(f"{AUTH_SERVICE_URL}/consumers")
            response.raise_for_status()
            consumers = response.json()

            print(f"✅ Found {len(consumers)} consumers:")
            for consumer in consumers:
                print(f"   - {consumer.get('username', 'N/A')} (ID: {consumer.get('id', 'N/A')})")

        except Exception as e:
            print(f"❌ Error listing consumers: {e}")

        print(f"\nExample completed!")
        print(f"\nTo manually test with curl:")
        print(f"curl -H 'Authorization: Bearer {jwt_token}' {KONG_GATEWAY_URL}{PROTECTED_SERVICE_PATH}")

if __name__ == "__main__":
    asyncio.run(main())