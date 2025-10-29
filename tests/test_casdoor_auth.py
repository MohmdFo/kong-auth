#!/usr/bin/env python3
"""
Test script for Casdoor authentication
This script demonstrates how to use the API with Casdoor authentication
"""

import json
import sys

import requests
import os
import pytest

# Configuration
BASE_URL = "http://localhost:8000"  # Adjust if your service runs on a different port

# Skip by default unless explicitly enabled
pytestmark = pytest.mark.skipif(
    os.getenv("ENABLE_INTEGRATION", "0") != "1",
    reason="Integration tests disabled; set ENABLE_INTEGRATION=1 to run.",
)


def test_without_auth():
    """Test endpoints without authentication (should fail)"""
    print("=== Testing without authentication ===")

    # Test root endpoint (should work - no auth required)
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"GET / - Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

    # Test protected endpoint (should fail)
    try:
        response = requests.get(f"{BASE_URL}/me")
        print(f"GET /me - Status: {response.status_code}")
        if response.status_code == 401:
            print("✅ Correctly rejected without authentication")
        else:
            print(f"❌ Unexpected response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

    # Test consumer list (should fail)
    try:
        response = requests.get(f"{BASE_URL}/consumers")
        print(f"GET /consumers - Status: {response.status_code}")
        if response.status_code == 401:
            print("✅ Correctly rejected without authentication")
        else:
            print(f"❌ Unexpected response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")


def test_with_auth(token):
    """Test endpoints with authentication"""
    print(f"\n=== Testing with authentication ===")

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # Test getting current user info
    try:
        response = requests.get(f"{BASE_URL}/me", headers=headers)
        print(f"GET /me - Status: {response.status_code}")
        if response.status_code == 200:
            user_info = response.json()
            print(f"✅ User authenticated: {user_info.get('name', 'Unknown')}")
            print(f"   Display Name: {user_info.get('display_name', 'N/A')}")
            print(f"   Email: {user_info.get('email', 'N/A')}")
            print(f"   Roles: {user_info.get('roles', [])}")
        else:
            print(f"❌ Failed to get user info: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

    # Test listing consumers
    try:
        response = requests.get(f"{BASE_URL}/consumers", headers=headers)
        print(f"GET /consumers - Status: {response.status_code}")
        if response.status_code == 200:
            consumers = response.json()
            print(f"✅ Retrieved {len(consumers)} consumers")
        else:
            print(f"❌ Failed to list consumers: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

    # Test creating a consumer
    try:
        consumer_data = {"username": f"test_user_{int(time.time())}"}
        response = requests.post(
            f"{BASE_URL}/create-consumer", headers=headers, json=consumer_data
        )
        print(f"POST /create-consumer - Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Consumer created: {result.get('username')}")
            print(f"   Consumer UUID: {result.get('consumer_uuid')}")
        else:
            print(f"❌ Failed to create consumer: {response.text}")
    except Exception as e:
        print(f"Error: {e}")


def main():
    """Main test function"""
    print("Casdoor Authentication Test")
    print("=" * 50)

    # Test without authentication
    test_without_auth()

    # Test with authentication (if token provided)
    if len(sys.argv) > 1:
        token = sys.argv[1]
        test_with_auth(token)
    else:
        print(f"\n=== To test with authentication ===")
        print("Run this script with a Casdoor token:")
        print(f"python {sys.argv[0]} <your_casdoor_token>")
        print("\nTo get a Casdoor token:")
        print("1. Login to your Casdoor instance")
        print("2. Go to your profile")
        print("3. Copy the access token")
        print("4. Use it as an argument to this script")


if __name__ == "__main__":
    import time

    main()
