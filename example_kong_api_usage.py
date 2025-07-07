#!/usr/bin/env python3
"""
Example usage of Kong Management API
Demonstrates how to use the new Kong service and route management endpoints
"""

import httpx
import asyncio
import json
import os
from typing import Dict, Any

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
KONG_ADMIN_URL = os.getenv("KONG_ADMIN_URL", "http://localhost:8006")

class KongAPIClient:
    """Client for interacting with the Kong Management API"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.client = httpx.AsyncClient()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to the API"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = await self.client.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json() if response.content else {}
        except httpx.HTTPStatusError as e:
            print(f"API error: {e.response.status_code} - {e.response.text}")
            raise e
    
    # Service Management
    async def create_service(self, service_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new service"""
        return await self._make_request("POST", "/kong/services", json=service_data)
    
    async def list_services(self) -> list:
        """List all services"""
        return await self._make_request("GET", "/kong/services")
    
    async def get_service(self, service_name: str) -> Dict[str, Any]:
        """Get a specific service"""
        return await self._make_request("GET", f"/kong/services/{service_name}")
    
    async def update_service(self, service_name: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a service"""
        return await self._make_request("PATCH", f"/kong/services/{service_name}", json=update_data)
    
    async def delete_service(self, service_name: str) -> Dict[str, Any]:
        """Delete a service"""
        return await self._make_request("DELETE", f"/kong/services/{service_name}")
    
    # Route Management
    async def create_route(self, route_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new route"""
        return await self._make_request("POST", "/kong/routes", json=route_data)
    
    async def list_routes(self, service_name: str = None) -> list:
        """List all routes, optionally filtered by service"""
        endpoint = "/kong/routes"
        if service_name:
            endpoint += f"?service_name={service_name}"
        return await self._make_request("GET", endpoint)
    
    async def get_route(self, route_name: str) -> Dict[str, Any]:
        """Get a specific route"""
        return await self._make_request("GET", f"/kong/routes/{route_name}")
    
    async def update_route(self, route_name: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a route"""
        return await self._make_request("PATCH", f"/kong/routes/{route_name}", json=update_data)
    
    async def delete_route(self, route_name: str) -> Dict[str, Any]:
        """Delete a route"""
        return await self._make_request("DELETE", f"/kong/routes/{route_name}")
    
    # Plugin Management
    async def enable_plugin(self, service_name: str, plugin_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enable a plugin on a service"""
        return await self._make_request("POST", f"/kong/services/{service_name}/plugins", json=plugin_data)
    
    async def list_plugins(self, service_name: str = None) -> list:
        """List all plugins, optionally filtered by service"""
        endpoint = "/kong/plugins"
        if service_name:
            endpoint += f"?service_name={service_name}"
        return await self._make_request("GET", endpoint)
    
    # Health and Status
    async def get_service_health(self, service_name: str) -> Dict[str, Any]:
        """Get service health information"""
        return await self._make_request("GET", f"/kong/services/{service_name}/health")
    
    async def get_kong_status(self) -> Dict[str, Any]:
        """Get Kong API status"""
        return await self._make_request("GET", "/kong/status")
    
    # Complete Service Setup
    async def setup_complete_service(self, complete_service_data: Dict[str, Any]) -> Dict[str, Any]:
        """Set up a complete service with routes and plugins"""
        return await self._make_request("POST", "/kong/services/complete", json=complete_service_data)


async def example_basic_service_management():
    """Example of basic service management operations"""
    print("🔧 Basic Service Management Example")
    print("=" * 50)
    
    async with KongAPIClient(API_BASE_URL) as client:
        # Check Kong status
        status = await client.get_kong_status()
        print(f"Kong Status: {status}")
        
        # Create a simple service
        service_data = {
            "name": "example-service",
            "url": "http://localhost:8001",
            "protocol": "http",
            "tags": ["example", "test"]
        }
        
        print(f"\n📝 Creating service: {service_data['name']}")
        service = await client.create_service(service_data)
        print(f"✅ Service created: {json.dumps(service, indent=2)}")
        
        # List all services
        print(f"\n📋 Listing all services:")
        services = await client.list_services()
        for svc in services:
            print(f"  - {svc['name']}: {svc.get('url', 'N/A')}")
        
        # Get specific service
        print(f"\n🔍 Getting service details:")
        service_details = await client.get_service("example-service")
        print(f"Service details: {json.dumps(service_details, indent=2)}")
        
        # Update service
        print(f"\n🔄 Updating service:")
        update_data = {
            "connect_timeout": 60000,
            "write_timeout": 60000,
            "read_timeout": 60000
        }
        updated_service = await client.update_service("example-service", update_data)
        print(f"✅ Service updated: {json.dumps(updated_service, indent=2)}")


async def example_route_management():
    """Example of route management operations"""
    print("\n🛣️  Route Management Example")
    print("=" * 50)
    
    async with KongAPIClient(API_BASE_URL) as client:
        # Create routes for the example service
        routes_data = [
            {
                "name": "example-service-main",
                "service_name": "example-service",
                "paths": ["/example"],
                "methods": ["GET", "POST", "OPTIONS"],
                "tags": ["main", "api"]
            },
            {
                "name": "example-service-api",
                "service_name": "example-service",
                "paths": ["/example/api"],
                "methods": ["GET", "POST", "PUT", "DELETE"],
                "tags": ["api", "rest"]
            },
            {
                "name": "example-service-status",
                "service_name": "example-service",
                "paths": ["/example/status"],
                "methods": ["GET"],
                "tags": ["status", "health"]
            }
        ]
        
        for route_data in routes_data:
            print(f"\n📝 Creating route: {route_data['name']}")
            route = await client.create_route(route_data)
            print(f"✅ Route created: {json.dumps(route, indent=2)}")
        
        # List routes for the service
        print(f"\n📋 Listing routes for example-service:")
        routes = await client.list_routes("example-service")
        for route in routes:
            print(f"  - {route['name']}: {route.get('paths', [])}")
        
        # Update a route
        print(f"\n🔄 Updating route:")
        update_data = {
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "strip_path": True
        }
        updated_route = await client.update_route("example-service-main", update_data)
        print(f"✅ Route updated: {json.dumps(updated_route, indent=2)}")


async def example_plugin_management():
    """Example of plugin management operations"""
    print("\n🔌 Plugin Management Example")
    print("=" * 50)
    
    async with KongAPIClient(API_BASE_URL) as client:
        # Enable JWT plugin
        jwt_plugin_data = {
            "name": "jwt",
            "config": {
                "uri_param_names": ["jwt"],
                "cookie_names": ["jwt"],
                "key_claim_name": "iss",
                "secret_is_base64": True,
                "claims_to_verify": ["exp"],
                "anonymous": None,
                "run_on_preflight": True,
                "maximum_expiration": 31536000,
                "header_names": ["authorization"]
            },
            "enabled": True,
            "tags": ["security", "jwt"]
        }
        
        print(f"\n🔐 Enabling JWT plugin on example-service:")
        jwt_plugin = await client.enable_plugin("example-service", jwt_plugin_data)
        print(f"✅ JWT plugin enabled: {json.dumps(jwt_plugin, indent=2)}")
        
        # Enable CORS plugin
        cors_plugin_data = {
            "name": "cors",
            "config": {
                "origins": ["*"],
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "headers": ["Content-Type", "Authorization"],
                "exposed_headers": ["X-Consumer-ID", "X-Consumer-Username"],
                "credentials": True,
                "max_age": 3600,
                "preflight_continue": False
            },
            "enabled": True,
            "tags": ["cors", "security"]
        }
        
        print(f"\n🌐 Enabling CORS plugin on example-service:")
        cors_plugin = await client.enable_plugin("example-service", cors_plugin_data)
        print(f"✅ CORS plugin enabled: {json.dumps(cors_plugin, indent=2)}")
        
        # List plugins for the service
        print(f"\n📋 Listing plugins for example-service:")
        plugins = await client.list_plugins("example-service")
        for plugin in plugins:
            print(f"  - {plugin['name']}: {plugin.get('enabled', False)}")


async def example_complete_service_setup():
    """Example of complete service setup with routes and plugins"""
    print("\n🚀 Complete Service Setup Example")
    print("=" * 50)
    
    async with KongAPIClient(API_BASE_URL) as client:
        complete_service_data = {
            "service": {
                "name": "complete-example-service",
                "url": "http://localhost:8002",
                "protocol": "http",
                "connect_timeout": 60000,
                "write_timeout": 60000,
                "read_timeout": 60000,
                "tags": ["complete", "example"]
            },
            "routes": [
                {
                    "name": "complete-service-main",
                    "service_name": "complete-example-service",
                    "paths": ["/complete"],
                    "methods": ["GET", "POST", "OPTIONS"],
                    "strip_path": True,
                    "tags": ["main"]
                },
                {
                    "name": "complete-service-admin",
                    "service_name": "complete-example-service",
                    "paths": ["/complete/admin"],
                    "methods": ["GET", "POST", "PUT", "DELETE"],
                    "strip_path": True,
                    "tags": ["admin"]
                }
            ],
            "plugins": [
                {
                    "name": "rate-limiting",
                    "config": {
                        "minute": 100,
                        "hour": 1000,
                        "policy": "local"
                    },
                    "enabled": True,
                    "tags": ["rate-limiting"]
                },
                {
                    "name": "cors",
                    "config": {
                        "origins": ["*"],
                        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                        "headers": ["Content-Type", "Authorization"],
                        "credentials": True
                    },
                    "enabled": True,
                    "tags": ["cors"]
                }
            ]
        }
        
        print(f"\n📝 Setting up complete service: {complete_service_data['service']['name']}")
        result = await client.setup_complete_service(complete_service_data)
        print(f"✅ Complete service setup: {json.dumps(result, indent=2)}")
        
        # Get service health
        print(f"\n🏥 Getting service health:")
        health = await client.get_service_health("complete-example-service")
        print(f"Service health: {json.dumps(health, indent=2)}")


async def example_cleanup():
    """Example of cleanup operations"""
    print("\n🧹 Cleanup Example")
    print("=" * 50)
    
    async with KongAPIClient(API_BASE_URL) as client:
        # Delete routes
        routes_to_delete = [
            "example-service-main",
            "example-service-api", 
            "example-service-status",
            "complete-service-main",
            "complete-service-admin"
        ]
        
        for route_name in routes_to_delete:
            try:
                print(f"\n🗑️  Deleting route: {route_name}")
                result = await client.delete_route(route_name)
                print(f"✅ Route deleted: {result}")
            except Exception as e:
                print(f"⚠️  Could not delete route {route_name}: {e}")
        
        # Delete services
        services_to_delete = [
            "example-service",
            "complete-example-service"
        ]
        
        for service_name in services_to_delete:
            try:
                print(f"\n🗑️  Deleting service: {service_name}")
                result = await client.delete_service(service_name)
                print(f"✅ Service deleted: {result}")
            except Exception as e:
                print(f"⚠️  Could not delete service {service_name}: {e}")


async def main():
    """Run all examples"""
    print("🎯 Kong Management API Examples")
    print("=" * 60)
    print(f"API Base URL: {API_BASE_URL}")
    print(f"Kong Admin URL: {KONG_ADMIN_URL}")
    print("=" * 60)
    
    try:
        # Run examples
        await example_basic_service_management()
        await example_route_management()
        await example_plugin_management()
        await example_complete_service_setup()
        
        # Uncomment the following line to run cleanup
        # await example_cleanup()
        
        print("\n✅ All examples completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main()) 