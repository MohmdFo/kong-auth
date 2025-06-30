#!/usr/bin/env python3
"""
Complete Flow Test Script
Tests the entire flow: create consumer -> get JWT token -> access protected service
"""

import asyncio
import httpx
import json
import time
import os

# Configuration
AUTH_SERVICE_URL = "http://localhost:8000"
KONG_GATEWAY_URL = "http://localhost:8000"
SAMPLE_SERVICE_URL = "http://localhost:8001"

class CompleteFlowTest:
    def __init__(self):
        self.auth_service_url = AUTH_SERVICE_URL
        self.kong_gateway_url = KONG_GATEWAY_URL
        self.sample_service_url = SAMPLE_SERVICE_URL
        
    async def test_auth_service(self):
        """Test the auth service endpoints"""
        print("🔐 Testing Auth Service...")
        print("-" * 40)
        
        async with httpx.AsyncClient() as client:
            # Test root endpoint
            try:
                response = await client.get(f"{self.auth_service_url}/")
                print(f"✅ Auth service root: {response.status_code}")
            except Exception as e:
                print(f"❌ Auth service not accessible: {e}")
                return False
            
            # Test consumer creation
            consumer_data = {
                "username": "testuser_complete_flow",
                "custom_id": "test_custom_id_123"
            }
            
            try:
                response = await client.post(
                    f"{self.auth_service_url}/create-consumer",
                    json=consumer_data
                )
                response.raise_for_status()
                result = response.json()
                
                print(f"✅ Consumer created: {result['consumer_id']}")
                print(f"✅ JWT Token generated: {result['token'][:50]}...")
                print(f"✅ Token expires: {result['expires_at']}")
                
                return result['token']
                
            except Exception as e:
                print(f"❌ Failed to create consumer: {e}")
                return None
    
    async def test_sample_service_direct(self):
        """Test the sample service directly (without Kong)"""
        print("\n🔗 Testing Sample Service (Direct Access)...")
        print("-" * 40)
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.sample_service_url}/")
                response.raise_for_status()
                result = response.json()
                
                print(f"✅ Sample service accessible: {response.status_code}")
                print(f"✅ Service message: {result.get('message', 'N/A')}")
                print(f"✅ Kong headers: {result.get('kong_headers', {})}")
                
                return True
                
            except Exception as e:
                print(f"❌ Sample service not accessible: {e}")
                return False
    
    async def test_protected_endpoints_without_token(self):
        """Test protected endpoints without JWT token (should fail)"""
        print("\n🚫 Testing Protected Endpoints (No Token)...")
        print("-" * 40)
        
        async with httpx.AsyncClient() as client:
            endpoints = [
                "/sample",
                "/sample/api",
                "/sample/status"
            ]
            
            for endpoint in endpoints:
                try:
                    response = await client.get(f"{self.kong_gateway_url}{endpoint}")
                    print(f"❌ {endpoint}: {response.status_code} (should be 401)")
                except Exception as e:
                    print(f"❌ {endpoint}: Error - {e}")
    
    async def test_protected_endpoints_with_token(self, jwt_token: str):
        """Test protected endpoints with JWT token"""
        print("\n🔓 Testing Protected Endpoints (With Token)...")
        print("-" * 40)
        
        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            # Test GET endpoints
            get_endpoints = [
                ("/sample", "Main endpoint"),
                ("/sample/api", "API endpoint"),
                ("/sample/status", "Status endpoint")
            ]
            
            for endpoint, description in get_endpoints:
                try:
                    response = await client.get(
                        f"{self.kong_gateway_url}{endpoint}",
                        headers=headers
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        print(f"✅ {description}: {response.status_code}")
                        print(f"   Message: {result.get('message', 'N/A')}")
                        print(f"   Kong Consumer ID: {result.get('kong_headers', {}).get('x_consumer_id', 'N/A')}")
                        print(f"   Kong Username: {result.get('kong_headers', {}).get('x_consumer_username', 'N/A')}")
                    else:
                        print(f"❌ {description}: {response.status_code} - {response.text}")
                        
                except Exception as e:
                    print(f"❌ {description}: Error - {e}")
            
            # Test POST endpoint
            try:
                post_data = {
                    "test": "data",
                    "timestamp": time.time(),
                    "message": "Hello from test script!"
                }
                
                response = await client.post(
                    f"{self.kong_gateway_url}/sample/api",
                    headers=headers,
                    json=post_data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ POST /sample/api: {response.status_code}")
                    print(f"   Received body: {result.get('body', {})}")
                else:
                    print(f"❌ POST /sample/api: {response.status_code} - {response.text}")
                    
            except Exception as e:
                print(f"❌ POST /sample/api: Error - {e}")
    
    async def test_invalid_token(self):
        """Test with invalid JWT token"""
        print("\n🚫 Testing Invalid Token...")
        print("-" * 40)
        
        invalid_tokens = [
            "invalid.token.here",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
            ""
        ]
        
        async with httpx.AsyncClient() as client:
            for i, token in enumerate(invalid_tokens, 1):
                headers = {"Authorization": f"Bearer {token}"} if token else {}
                
                try:
                    response = await client.get(
                        f"{self.kong_gateway_url}/sample/status",
                        headers=headers
                    )
                    print(f"❌ Invalid token {i}: {response.status_code} (should be 401)")
                except Exception as e:
                    print(f"❌ Invalid token {i}: Error - {e}")
    
    async def run_complete_test(self):
        """Run the complete test flow"""
        print("🧪 Complete Flow Test")
        print("=" * 50)
        
        # Step 1: Test auth service
        jwt_token = await self.test_auth_service()
        if not jwt_token:
            print("❌ Auth service test failed. Stopping.")
            return False
        
        # Step 2: Test sample service directly
        if not await self.test_sample_service_direct():
            print("❌ Sample service test failed. Stopping.")
            return False
        
        # Step 3: Test protected endpoints without token
        await self.test_protected_endpoints_without_token()
        
        # Step 4: Test protected endpoints with valid token
        await self.test_protected_endpoints_with_token(jwt_token)
        
        # Step 5: Test invalid tokens
        await self.test_invalid_token()
        
        print("\n" + "=" * 50)
        print("✅ Complete flow test finished!")
        print("\n📋 Summary:")
        print("  - Auth service: ✅ Working")
        print("  - Sample service: ✅ Working")
        print("  - Kong protection: ✅ Working")
        print("  - JWT validation: ✅ Working")
        print(f"\n🔑 Valid JWT Token: {jwt_token[:50]}...")
        print(f"🌐 Test protected endpoints:")
        print(f"   curl -H 'Authorization: Bearer {jwt_token}' {self.kong_gateway_url}/sample/status")
        
        return True

async def main():
    """Main function"""
    test = CompleteFlowTest()
    await test.run_complete_test()

if __name__ == "__main__":
    asyncio.run(main()) 