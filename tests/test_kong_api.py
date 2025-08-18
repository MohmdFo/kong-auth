#!/usr/bin/env python3
"""
Test script for Kong Management API
Tests basic functionality of the new Kong service and route management endpoints
"""

import asyncio
import json
import os
import sys
from typing import Any, Dict

import httpx

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
KONG_ADMIN_URL = os.getenv("KONG_ADMIN_URL", "http://localhost:8006")


class KongAPITester:
    """Test client for Kong Management API"""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient()
        self.test_results = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    async def _make_request(
        self, method: str, endpoint: str, **kwargs
    ) -> Dict[str, Any]:
        """Make HTTP request to the API"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = await self.client.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json() if response.content else {}
        except httpx.HTTPStatusError as e:
            print(f"❌ API error: {e.response.status_code} - {e.response.text}")
            raise e

    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")
        self.test_results.append(
            {"test": test_name, "success": success, "details": details}
        )

    async def test_kong_status(self):
        """Test Kong status endpoint"""
        try:
            status = await self._make_request("GET", "/kong/status")
            if "status" in status:
                if status["status"] == "healthy":
                    self.log_test("Kong Status", True, f"Status: {status['status']}")
                    return True
                else:
                    self.log_test(
                        "Kong Status",
                        False,
                        f"Kong unhealthy: {status.get('error', 'Unknown error')}",
                    )
                    return False
            else:
                self.log_test("Kong Status", False, "Invalid response format")
                return False
        except Exception as e:
            self.log_test("Kong Status", False, str(e))
            return False

    async def test_create_service(self):
        """Test service creation"""
        try:
            service_data = {
                "name": "test-service",
                "url": "http://localhost:8001",
                "protocol": "http",
                "tags": ["test"],
            }

            service = await self._make_request(
                "POST", "/kong/services", json=service_data
            )
            if service.get("name") == "test-service":
                self.log_test(
                    "Create Service", True, f"Service created: {service['name']}"
                )
                return True
            else:
                self.log_test("Create Service", False, "Service creation failed")
                return False
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 503:
                self.log_test(
                    "Create Service",
                    False,
                    "Kong Admin API not accessible - Kong may not be running",
                )
                return False
            else:
                self.log_test(
                    "Create Service",
                    False,
                    f"HTTP {e.response.status_code}: {e.response.text}",
                )
                return False
        except Exception as e:
            self.log_test("Create Service", False, str(e))
            return False

    async def test_list_services(self):
        """Test listing services"""
        try:
            services = await self._make_request("GET", "/kong/services")
            if isinstance(services, list):
                test_service = next(
                    (s for s in services if s.get("name") == "test-service"), None
                )
                if test_service:
                    self.log_test(
                        "List Services", True, f"Found {len(services)} services"
                    )
                    return True
                else:
                    self.log_test(
                        "List Services", False, "Test service not found in list"
                    )
                    return False
            else:
                self.log_test("List Services", False, "Invalid response format")
                return False
        except Exception as e:
            self.log_test("List Services", False, str(e))
            return False

    async def test_get_service(self):
        """Test getting a specific service"""
        try:
            service = await self._make_request("GET", "/kong/services/test-service")
            if service.get("name") == "test-service":
                self.log_test(
                    "Get Service", True, f"Service retrieved: {service['name']}"
                )
                return True
            else:
                self.log_test("Get Service", False, "Service retrieval failed")
                return False
        except Exception as e:
            self.log_test("Get Service", False, str(e))
            return False

    async def test_create_route(self):
        """Test route creation"""
        try:
            route_data = {
                "name": "test-route",
                "service_name": "test-service",
                "paths": ["/test"],
                "methods": ["GET", "POST"],
                "tags": ["test"],
            }

            route = await self._make_request("POST", "/kong/routes", json=route_data)
            if route.get("name") == "test-route":
                self.log_test("Create Route", True, f"Route created: {route['name']}")
                return True
            else:
                self.log_test("Create Route", False, "Route creation failed")
                return False
        except Exception as e:
            self.log_test("Create Route", False, str(e))
            return False

    async def test_list_routes(self):
        """Test listing routes"""
        try:
            routes = await self._make_request("GET", "/kong/routes")
            if isinstance(routes, list):
                test_route = next(
                    (r for r in routes if r.get("name") == "test-route"), None
                )
                if test_route:
                    self.log_test("List Routes", True, f"Found {len(routes)} routes")
                    return True
                else:
                    self.log_test("List Routes", False, "Test route not found in list")
                    return False
            else:
                self.log_test("List Routes", False, "Invalid response format")
                return False
        except Exception as e:
            self.log_test("List Routes", False, str(e))
            return False

    async def test_enable_plugin(self):
        """Test plugin enabling"""
        try:
            plugin_data = {
                "name": "cors",
                "config": {
                    "origins": ["*"],
                    "methods": ["GET", "POST"],
                    "headers": ["Content-Type"],
                    "credentials": True,
                },
                "enabled": True,
                "tags": ["test"],
            }

            plugin = await self._make_request(
                "POST", "/kong/services/test-service/plugins", json=plugin_data
            )
            if plugin.get("name") == "cors":
                self.log_test(
                    "Enable Plugin", True, f"Plugin enabled: {plugin['name']}"
                )
                return True
            else:
                self.log_test("Enable Plugin", False, "Plugin enabling failed")
                return False
        except Exception as e:
            self.log_test("Enable Plugin", False, str(e))
            return False

    async def test_service_health(self):
        """Test service health endpoint"""
        try:
            health = await self._make_request(
                "GET", "/kong/services/test-service/health"
            )
            if "service" in health and "routes" in health and "plugins" in health:
                self.log_test(
                    "Service Health",
                    True,
                    f"Health status: {health.get('status', 'unknown')}",
                )
                return True
            else:
                self.log_test("Service Health", False, "Invalid health response format")
                return False
        except Exception as e:
            self.log_test("Service Health", False, str(e))
            return False

    async def test_complete_service_setup(self):
        """Test complete service setup"""
        try:
            complete_data = {
                "service": {
                    "name": "complete-test-service",
                    "url": "http://localhost:8002",
                    "protocol": "http",
                    "tags": ["test", "complete"],
                },
                "routes": [
                    {
                        "name": "complete-test-route",
                        "service_name": "complete-test-service",
                        "paths": ["/complete"],
                        "methods": ["GET", "POST"],
                        "tags": ["test"],
                    }
                ],
                "plugins": [
                    {
                        "name": "rate-limiting",
                        "config": {"minute": 10, "hour": 100, "policy": "local"},
                        "enabled": True,
                        "tags": ["test"],
                    }
                ],
            }

            result = await self._make_request(
                "POST", "/kong/services/complete", json=complete_data
            )
            if result.get("status") == "success":
                self.log_test(
                    "Complete Service Setup", True, "Complete service setup successful"
                )
                return True
            else:
                self.log_test(
                    "Complete Service Setup", False, "Complete service setup failed"
                )
                return False
        except Exception as e:
            self.log_test("Complete Service Setup", False, str(e))
            return False

    async def test_cleanup(self):
        """Test cleanup operations"""
        try:
            # Delete routes
            await self._make_request("DELETE", "/kong/routes/test-route")
            await self._make_request("DELETE", "/kong/routes/complete-test-route")

            # Delete services
            await self._make_request("DELETE", "/kong/services/test-service")
            await self._make_request("DELETE", "/kong/services/complete-test-service")

            self.log_test("Cleanup", True, "Test resources cleaned up")
            return True
        except Exception as e:
            self.log_test("Cleanup", False, str(e))
            return False

    async def run_all_tests(self):
        """Run all tests"""
        print("🧪 Running Kong Management API Tests")
        print("=" * 50)
        print(f"API Base URL: {self.base_url}")
        print(f"Kong Admin URL: {KONG_ADMIN_URL}")
        print("=" * 50)

        tests = [
            ("Kong Status", self.test_kong_status),
            ("Create Service", self.test_create_service),
            ("List Services", self.test_list_services),
            ("Get Service", self.test_get_service),
            ("Create Route", self.test_create_route),
            ("List Routes", self.test_list_routes),
            ("Enable Plugin", self.test_enable_plugin),
            ("Service Health", self.test_service_health),
            ("Complete Service Setup", self.test_complete_service_setup),
            ("Cleanup", self.test_cleanup),
        ]

        for test_name, test_func in tests:
            print(f"\n🔍 Running: {test_name}")
            try:
                await test_func()
            except Exception as e:
                self.log_test(test_name, False, f"Test failed with exception: {e}")

        # Print summary
        print("\n" + "=" * 50)
        print("📊 Test Summary")
        print("=" * 50)

        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)

        for result in self.test_results:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"{status} {result['test']}")
            if result["details"]:
                print(f"   {result['details']}")

        print(f"\n📈 Results: {passed}/{total} tests passed")

        if passed == total:
            print("🎉 All tests passed!")
            return True
        else:
            print("⚠️  Some tests failed!")
            return False


async def main():
    """Main test function"""
    try:
        async with KongAPITester(API_BASE_URL) as tester:
            success = await tester.run_all_tests()

            # Check if Kong is not running
            if not success:
                print("\n" + "=" * 60)
                print("🔧 Troubleshooting")
                print("=" * 60)
                print(
                    "If tests are failing due to connection errors, Kong may not be running."
                )
                print("")
                print("To start Kong for testing:")
                print("1. Run: ./start-kong-for-testing.sh")
                print(
                    "2. Or manually: docker-compose -f kong/docker-compose.kong.yml up -d"
                )
                print("3. Wait for Kong to be ready, then run tests again")
                print("")
                print("To check Kong status:")
                print("   curl http://localhost:8006/status")
                print("")

            sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test runner failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
