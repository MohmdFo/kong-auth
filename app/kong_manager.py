"""
Kong Manager Module
Provides a clean interface for managing Kong services and routes
"""

import httpx
import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, field_validator
import os

logger = logging.getLogger(__name__)

# Kong configuration
KONG_ADMIN_URL = os.getenv("KONG_ADMIN_URL", "http://localhost:8006")


class ServiceConfig(BaseModel):
    """Configuration for creating a Kong service"""
    name: str
    url: str  # Changed from HttpUrl to str for better compatibility
    protocol: str = "http"
    host: Optional[str] = None
    port: Optional[int] = None
    path: Optional[str] = None
    retries: Optional[int] = None
    connect_timeout: Optional[int] = None
    write_timeout: Optional[int] = None
    read_timeout: Optional[int] = None
    tags: Optional[List[str]] = None

    @field_validator('url')
    @classmethod
    def validate_url(cls, v):
        """Validate URL format"""
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v


class RouteConfig(BaseModel):
    """Configuration for creating a Kong route"""
    name: str
    service_name: str
    paths: Optional[List[str]] = None
    protocols: Optional[List[str]] = None
    methods: Optional[List[str]] = None
    hosts: Optional[List[str]] = None
    headers: Optional[Dict[str, List[str]]] = None
    https_redirect_status_code: Optional[int] = None
    regex_priority: Optional[int] = None
    strip_path: Optional[bool] = None
    preserve_host: Optional[bool] = None
    request_buffering: Optional[bool] = None
    response_buffering: Optional[bool] = None
    tags: Optional[List[str]] = None


class PluginConfig(BaseModel):
    """Configuration for enabling Kong plugins"""
    name: str
    config: Dict[str, Any]
    enabled: bool = True
    tags: Optional[List[str]] = None


class KongManager:
    """Manages Kong services, routes, and plugins"""

    def __init__(self, admin_url: str = KONG_ADMIN_URL):
        self.admin_url = admin_url.rstrip('/')
        self.client = httpx.AsyncClient()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to Kong Admin API"""
        url = f"{self.admin_url}{endpoint}"
        try:
            response = await self.client.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json() if response.content else {}
        except httpx.HTTPStatusError as e:
            logger.error(f"Kong API error: {e.response.status_code} - {e.response.text}")
            raise e
        except httpx.ConnectError as e:
            logger.error(f"Kong connection error: {e}")
            raise ConnectionError(f"Cannot connect to Kong Admin API at {self.admin_url}. Please ensure Kong is running and accessible.")
        except httpx.TimeoutException as e:
            logger.error(f"Kong timeout error: {e}")
            raise TimeoutError(f"Request to Kong Admin API timed out: {e}")
        except Exception as e:
            logger.error(f"Unexpected error communicating with Kong: {e}")
            raise Exception(f"Failed to communicate with Kong Admin API: {e}")

    async def create_service(self, config: ServiceConfig) -> Dict[str, Any]:
        """Create a service in Kong"""
        service_data = config.model_dump(exclude_none=True)

        try:
            service = await self._make_request("POST", "/services/", json=service_data)
            logger.info(f"✅ Service '{config.name}' created successfully")
            return service
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 409:
                # Service already exists, get it
                service = await self._make_request("GET", f"/services/{config.name}")
                logger.info(f"ℹ️  Service '{config.name}' already exists")
                return service
            else:
                logger.error(f"❌ Failed to create service '{config.name}': {e.response.text}")
                raise

    async def get_service(self, service_name: str) -> Dict[str, Any]:
        """Get a service by name"""
        try:
            service = await self._make_request("GET", f"/services/{service_name}")
            return service
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise ValueError(f"Service '{service_name}' not found")
            raise

    async def list_services(self) -> List[Dict[str, Any]]:
        """List all services"""
        services = await self._make_request("GET", "/services/")
        return services.get("data", [])

    async def update_service(self, service_name: str, config: ServiceConfig) -> Dict[str, Any]:
        """Update a service"""
        service_data = config.model_dump(exclude_none=True)
        service = await self._make_request("PATCH", f"/services/{service_name}", json=service_data)
        logger.info(f"✅ Service '{service_name}' updated successfully")
        return service

    async def delete_service(self, service_name: str) -> Dict[str, Any]:
        """Delete a service"""
        await self._make_request("DELETE", f"/services/{service_name}")
        logger.info(f"✅ Service '{service_name}' deleted successfully")
        return {"message": f"Service '{service_name}' deleted successfully"}

    async def create_route(self, config: RouteConfig) -> Dict[str, Any]:
        """Create a route in Kong"""
        route_data = config.model_dump(exclude_none=True)
        # Kong expects service as an object with name/id
        route_data["service"] = {"name": config.service_name}
        del route_data["service_name"]

        try:
            route = await self._make_request("POST", "/routes/", json=route_data)
            logger.info(f"✅ Route '{config.name}' created successfully")
            return route
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 409:
                # Route already exists, get it
                route = await self._make_request("GET", f"/routes/{config.name}")
                logger.info(f"ℹ️  Route '{config.name}' already exists")
                return route
            else:
                logger.error(f"❌ Failed to create route '{config.name}': {e.response.text}")
                raise

    async def get_route(self, route_name: str) -> Dict[str, Any]:
        """Get a route by name"""
        try:
            route = await self._make_request("GET", f"/routes/{route_name}")
            return route
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise ValueError(f"Route '{route_name}' not found")
            raise

    async def list_routes(self, service_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all routes, optionally filtered by service"""
        endpoint = "/routes/"
        if service_name:
            endpoint = f"/services/{service_name}/routes/"

        routes = await self._make_request("GET", endpoint)
        return routes.get("data", [])

    async def update_route(self, route_name: str, config: RouteConfig) -> Dict[str, Any]:
        """Update a route"""
        route_data = config.model_dump(exclude_none=True)
        if "service_name" in route_data:
            route_data["service"] = {"name": route_data.pop("service_name")}

        route = await self._make_request("PATCH", f"/routes/{route_name}", json=route_data)
        logger.info(f"✅ Route '{route_name}' updated successfully")
        return route

    async def delete_route(self, route_name: str) -> Dict[str, Any]:
        """Delete a route"""
        await self._make_request("DELETE", f"/routes/{route_name}")
        logger.info(f"✅ Route '{route_name}' deleted successfully")
        return {"message": f"Route '{route_name}' deleted successfully"}

    async def enable_plugin(self, service_name: str, config: PluginConfig) -> Dict[str, Any]:
        """Enable a plugin on a service"""
        plugin_data = config.model_dump(exclude_none=True)

        try:
            plugin = await self._make_request("POST", f"/services/{service_name}/plugins", json=plugin_data)
            logger.info(f"✅ Plugin '{config.name}' enabled on service '{service_name}'")
            return plugin
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 409:
                logger.info(f"ℹ️  Plugin '{config.name}' already enabled on service '{service_name}'")
                return {"message": "Plugin already exists"}
            else:
                logger.error(f"❌ Failed to enable plugin '{config.name}': {e.response.text}")
                raise

    async def list_plugins(self, service_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """List plugins, optionally filtered by service"""
        endpoint = "/plugins/"
        if service_name:
            endpoint = f"/services/{service_name}/plugins/"

        plugins = await self._make_request("GET", endpoint)
        return plugins.get("data", [])

    async def delete_plugin(self, plugin_id: str) -> Dict[str, Any]:
        """Delete a plugin"""
        await self._make_request("DELETE", f"/plugins/{plugin_id}")
        logger.info(f"✅ Plugin '{plugin_id}' deleted successfully")
        return {"message": f"Plugin '{plugin_id}' deleted successfully"}

    async def get_service_health(self, service_name: str) -> Dict[str, Any]:
        """Get service health information"""
        try:
            # Get service details
            service = await self.get_service(service_name)

            # Get routes for this service
            routes = await self.list_routes(service_name)

            # Get plugins for this service
            plugins = await self.list_plugins(service_name)

            return {
                "service": service,
                "routes": routes,
                "plugins": plugins,
                "status": "healthy" if service else "unhealthy"
            }
        except Exception as e:
            logger.error(f"Failed to get health for service '{service_name}': {e}")
            return {
                "service": None,
                "routes": [],
                "plugins": [],
                "status": "error",
                "error": str(e)
            }

    async def setup_complete_service(
            self, service_config: ServiceConfig,
            route_configs: List[RouteConfig],
            plugin_configs: Optional[List[PluginConfig]] = None
            ) -> Dict[str, Any]:
        """Set up a complete service with routes and plugins"""
        logger.info(f"🚀 Setting up complete service: {service_config.name}")

        try:
            # Create service
            service = await self.create_service(service_config)

            # Create routes
            routes = []
            for route_config in route_configs:
                route = await self.create_route(route_config)
                routes.append(route)

            # Enable plugins
            plugins = []
            if plugin_configs:
                for plugin_config in plugin_configs:
                    plugin = await self.enable_plugin(service_config.name, plugin_config)
                    plugins.append(plugin)

            logger.info(f"✅ Complete service setup finished for '{service_config.name}'")

            return {
                "service": service,
                "routes": routes,
                "plugins": plugins,
                "status": "success"
            }

        except Exception as e:
            logger.error(f"❌ Failed to setup complete service '{service_config.name}': {e}")
            raise
