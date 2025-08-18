#!/usr/bin/env python3
"""
Kong Setup Script
Automatically creates services and routes in Kong for testing JWT authentication
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict

import httpx

# Add parent directory to path to import logging_config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.logging_config import setup_logging

# Setup logging
logger = setup_logging()

# Kong configuration
KONG_ADMIN_URL = os.getenv("KONG_ADMIN_URL", "http://localhost:8006")
SAMPLE_SERVICE_URL = os.getenv("SAMPLE_SERVICE_URL", "http://localhost:8001")


class KongSetup:
    def __init__(self, admin_url: str):
        self.admin_url = admin_url.rstrip("/")

    async def create_service(self, name: str, url: str) -> Dict[str, Any]:
        """Create a service in Kong"""
        async with httpx.AsyncClient() as client:
            service_data = {"name": name, "url": url, "protocol": "http"}

            try:
                response = await client.post(
                    f"{self.admin_url}/services/", json=service_data
                )
                response.raise_for_status()
                service = response.json()
                logger.info(f"✅ Service '{name}' created successfully")
                return service
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 409:
                    # Service already exists, get it
                    response = await client.get(f"{self.admin_url}/services/{name}")
                    response.raise_for_status()
                    service = response.json()
                    logger.info(f"ℹ️  Service '{name}' already exists")
                    return service
                else:
                    logger.error(
                        f"❌ Failed to create service '{name}': {e.response.text}"
                    )
                    raise

    async def create_route(
        self, service_name: str, name: str, paths: list, methods: list = None
    ) -> Dict[str, Any]:
        """Create a route in Kong"""
        async with httpx.AsyncClient() as client:
            route_data = {
                "name": name,
                "paths": paths,
                "service": {"name": service_name},
            }

            if methods:
                route_data["methods"] = methods

            try:
                response = await client.post(
                    f"{self.admin_url}/routes/", json=route_data
                )
                response.raise_for_status()
                route = response.json()
                logger.info(f"✅ Route '{name}' created successfully")
                return route
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 409:
                    # Route already exists, get it
                    response = await client.get(f"{self.admin_url}/routes/{name}")
                    response.raise_for_status()
                    route = response.json()
                    logger.info(f"ℹ️  Route '{name}' already exists")
                    return route
                else:
                    logger.error(
                        f"❌ Failed to create route '{name}': {e.response.text}"
                    )
                    raise

    async def enable_jwt_plugin(self, service_name: str) -> Dict[str, Any]:
        """Enable JWT plugin on a service"""
        async with httpx.AsyncClient() as client:
            plugin_data = {
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
                    "header_names": ["authorization"],
                },
            }

            try:
                response = await client.post(
                    f"{self.admin_url}/services/{service_name}/plugins",
                    json=plugin_data,
                )
                response.raise_for_status()
                plugin = response.json()
                logger.info(f"✅ JWT plugin enabled on service '{service_name}'")
                return plugin
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 409:
                    logger.info(
                        f"ℹ️  JWT plugin already enabled on service '{service_name}'"
                    )
                    return {"message": "Plugin already exists"}
                else:
                    logger.error(f"❌ Failed to enable JWT plugin: {e.response.text}")
                    raise

    async def enable_cors_plugin(self, service_name: str) -> Dict[str, Any]:
        """Enable CORS plugin on a service"""
        async with httpx.AsyncClient() as client:
            plugin_data = {
                "name": "cors",
                "config": {
                    "origins": ["*"],
                    "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                    "headers": ["Content-Type", "Authorization"],
                    "exposed_headers": ["X-Consumer-ID", "X-Consumer-Username"],
                    "credentials": True,
                    "max_age": 3600,
                    "preflight_continue": False,
                },
            }

            try:
                response = await client.post(
                    f"{self.admin_url}/services/{service_name}/plugins",
                    json=plugin_data,
                )
                response.raise_for_status()
                plugin = response.json()
                logger.info(f"✅ CORS plugin enabled on service '{service_name}'")
                return plugin
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 409:
                    logger.info(
                        f"ℹ️  CORS plugin already enabled on service '{service_name}'"
                    )
                    return {"message": "Plugin already exists"}
                else:
                    logger.error(f"❌ Failed to enable CORS plugin: {e.response.text}")
                    raise

    async def setup_sample_service(self):
        """Set up the complete sample service configuration"""
        logger.info("🚀 Setting up Kong sample service...")
        logger.info(f"Kong Admin URL: {self.admin_url}")
        logger.info(f"Sample Service URL: {SAMPLE_SERVICE_URL}")
        logger.info("-" * 50)

        try:
            # Create service
            service = await self.create_service("sample-service", SAMPLE_SERVICE_URL)

            # Create routes
            routes = []

            # Main route
            main_route = await self.create_route(
                service_name="sample-service",
                name="sample-service-main",
                paths=["/sample"],
                methods=["GET", "POST", "OPTIONS"],
            )
            routes.append(main_route)

            # API route
            api_route = await self.create_route(
                service_name="sample-service",
                name="sample-service-api",
                paths=["/sample/api"],
                methods=["GET", "POST", "OPTIONS"],
            )
            routes.append(api_route)

            # Status route
            status_route = await self.create_route(
                service_name="sample-service",
                name="sample-service-status",
                paths=["/sample/status"],
                methods=["GET", "OPTIONS"],
            )
            routes.append(status_route)

            # Enable plugins
            await self.enable_jwt_plugin("sample-service")
            await self.enable_cors_plugin("sample-service")

            logger.info("✅ Kong setup completed successfully!")
            logger.info("📋 Available endpoints:")
            logger.info(f"  Kong Gateway: http://localhost:8000")
            logger.info(f"  Protected endpoints:")
            logger.info(f"    GET/POST  http://localhost:8000/sample")
            logger.info(f"    GET/POST  http://localhost:8000/sample/api")
            logger.info(f"    GET       http://localhost:8000/sample/status")
            logger.info(f"🔐 All endpoints require JWT authentication")
            logger.info(f"📝 Use your auth service to get JWT tokens")

            return {"service": service, "routes": routes}

        except Exception as e:
            logger.error(f"❌ Setup failed: {e}")
            raise

    async def cleanup(self):
        """Clean up Kong configuration"""
        logger.info("🧹 Cleaning up Kong configuration...")

        async with httpx.AsyncClient() as client:
            # Delete routes
            routes_to_delete = [
                "sample-service-main",
                "sample-service-api",
                "sample-service-status",
            ]

            for route_name in routes_to_delete:
                try:
                    await client.delete(f"{self.admin_url}/routes/{route_name}")
                    logger.info(f"✅ Deleted route '{route_name}'")
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 404:
                        logger.info(f"ℹ️  Route '{route_name}' not found")
                    else:
                        logger.error(
                            f"❌ Failed to delete route '{route_name}': {e.response.text}"
                        )

            # Delete service
            try:
                await client.delete(f"{self.admin_url}/services/sample-service")
                logger.info("✅ Deleted service 'sample-service'")
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    logger.info("ℹ️  Service 'sample-service' not found")
                else:
                    logger.error(f"❌ Failed to delete service: {e.response.text}")


async def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="Kong Setup Script")
    parser.add_argument(
        "--cleanup", action="store_true", help="Clean up Kong configuration"
    )
    parser.add_argument("--admin-url", default=KONG_ADMIN_URL, help="Kong Admin URL")
    parser.add_argument(
        "--service-url", default=SAMPLE_SERVICE_URL, help="Sample service URL"
    )

    args = parser.parse_args()

    # Update environment variables
    os.environ["KONG_ADMIN_URL"] = args.admin_url
    os.environ["SAMPLE_SERVICE_URL"] = args.service_url

    kong_setup = KongSetup(args.admin_url)

    if args.cleanup:
        await kong_setup.cleanup()
    else:
        await kong_setup.setup_sample_service()


if __name__ == "__main__":
    asyncio.run(main())
