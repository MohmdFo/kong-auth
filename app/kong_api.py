"""
Kong Management API
REST API endpoints for managing Kong services and routes
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from .casdoor_auth import CasdoorUser, get_current_user
from .kong_manager import KongManager, PluginConfig, RouteConfig, ServiceConfig

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/kong", tags=["Kong Management"])


# Request/Response Models
class ServiceCreateRequest(BaseModel):
    name: str
    url: str
    protocol: str = "http"
    host: Optional[str] = None
    port: Optional[int] = None
    path: Optional[str] = None
    retries: Optional[int] = None
    connect_timeout: Optional[int] = None
    write_timeout: Optional[int] = None
    read_timeout: Optional[int] = None
    tags: Optional[List[str]] = None


class ServiceUpdateRequest(BaseModel):
    url: Optional[str] = None
    protocol: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    path: Optional[str] = None
    retries: Optional[int] = None
    connect_timeout: Optional[int] = None
    write_timeout: Optional[int] = None
    read_timeout: Optional[int] = None
    tags: Optional[List[str]] = None


class RouteCreateRequest(BaseModel):
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


class RouteUpdateRequest(BaseModel):
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


class PluginCreateRequest(BaseModel):
    name: str
    config: Dict[str, Any]
    enabled: bool = True
    tags: Optional[List[str]] = None


class CompleteServiceRequest(BaseModel):
    service: ServiceCreateRequest
    routes: List[RouteCreateRequest]
    plugins: Optional[List[PluginCreateRequest]] = None


class ServiceHealthResponse(BaseModel):
    service: Optional[Dict[str, Any]]
    routes: List[Dict[str, Any]]
    plugins: List[Dict[str, Any]]
    status: str
    error: Optional[str] = None


# Dependency
async def get_kong_manager() -> KongManager:
    """Dependency to get Kong manager instance"""
    async with KongManager() as manager:
        yield manager


# Service Management Endpoints
@router.post("/services", response_model=Dict[str, Any])
async def create_service(
    request: ServiceCreateRequest,
    manager: KongManager = Depends(get_kong_manager),
    current_user: CasdoorUser = Depends(get_current_user),
):
    """Create a new Kong service"""
    try:
        service_config = ServiceConfig(**request.model_dump())
        service = await manager.create_service(service_config)
        return service
    except ConnectionError as e:
        logger.error(f"Connection error creating service: {e}")
        raise HTTPException(
            status_code=503, detail=f"Kong Admin API not accessible: {str(e)}"
        )
    except TimeoutError as e:
        logger.error(f"Timeout error creating service: {e}")
        raise HTTPException(status_code=504, detail=f"Kong Admin API timeout: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to create service: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/services", response_model=List[Dict[str, Any]])
async def list_services(
    manager: KongManager = Depends(get_kong_manager),
    current_user: CasdoorUser = Depends(get_current_user),
):
    """List all Kong services"""
    try:
        services = await manager.list_services()
        return services
    except ConnectionError as e:
        logger.error(f"Connection error listing services: {e}")
        raise HTTPException(
            status_code=503, detail=f"Kong Admin API not accessible: {str(e)}"
        )
    except TimeoutError as e:
        logger.error(f"Timeout error listing services: {e}")
        raise HTTPException(status_code=504, detail=f"Kong Admin API timeout: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to list services: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/services/{service_name}", response_model=Dict[str, Any])
async def get_service(
    service_name: str,
    manager: KongManager = Depends(get_kong_manager),
    current_user: CasdoorUser = Depends(get_current_user),
):
    """Get a specific Kong service"""
    try:
        service = await manager.get_service(service_name)
        return service
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ConnectionError as e:
        logger.error(f"Connection error getting service {service_name}: {e}")
        raise HTTPException(
            status_code=503, detail=f"Kong Admin API not accessible: {str(e)}"
        )
    except TimeoutError as e:
        logger.error(f"Timeout error getting service {service_name}: {e}")
        raise HTTPException(status_code=504, detail=f"Kong Admin API timeout: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to get service {service_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/services/{service_name}", response_model=Dict[str, Any])
async def update_service(
    service_name: str,
    request: ServiceUpdateRequest,
    manager: KongManager = Depends(get_kong_manager),
    current_user: CasdoorUser = Depends(get_current_user),
):
    """Update a Kong service"""
    try:
        # Get current service to merge with updates
        current_service = await manager.get_service(service_name)

        # Create service config with merged data
        update_data = request.model_dump(exclude_none=True)
        service_config = ServiceConfig(
            name=service_name,
            url=update_data.get("url", current_service.get("url", "")),
            protocol=update_data.get(
                "protocol", current_service.get("protocol", "http")
            ),
            host=update_data.get("host", current_service.get("host")),
            port=update_data.get("port", current_service.get("port")),
            path=update_data.get("path", current_service.get("path")),
            retries=update_data.get("retries", current_service.get("retries")),
            connect_timeout=update_data.get(
                "connect_timeout", current_service.get("connect_timeout")
            ),
            write_timeout=update_data.get(
                "write_timeout", current_service.get("write_timeout")
            ),
            read_timeout=update_data.get(
                "read_timeout", current_service.get("read_timeout")
            ),
            tags=update_data.get("tags", current_service.get("tags")),
        )

        service = await manager.update_service(service_name, service_config)
        return service
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ConnectionError as e:
        logger.error(f"Connection error updating service {service_name}: {e}")
        raise HTTPException(
            status_code=503, detail=f"Kong Admin API not accessible: {str(e)}"
        )
    except TimeoutError as e:
        logger.error(f"Timeout error updating service {service_name}: {e}")
        raise HTTPException(status_code=504, detail=f"Kong Admin API timeout: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to update service {service_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/services/{service_name}", response_model=Dict[str, Any])
async def delete_service(
    service_name: str,
    manager: KongManager = Depends(get_kong_manager),
    current_user: CasdoorUser = Depends(get_current_user),
):
    """Delete a Kong service"""
    try:
        result = await manager.delete_service(service_name)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ConnectionError as e:
        logger.error(f"Connection error deleting service {service_name}: {e}")
        raise HTTPException(
            status_code=503, detail=f"Kong Admin API not accessible: {str(e)}"
        )
    except TimeoutError as e:
        logger.error(f"Timeout error deleting service {service_name}: {e}")
        raise HTTPException(status_code=504, detail=f"Kong Admin API timeout: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to delete service {service_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Route Management Endpoints
@router.post("/routes", response_model=Dict[str, Any])
async def create_route(
    request: RouteCreateRequest,
    manager: KongManager = Depends(get_kong_manager),
    current_user: CasdoorUser = Depends(get_current_user),
):
    """Create a new Kong route"""
    try:
        route_config = RouteConfig(**request.model_dump())
        route = await manager.create_route(route_config)
        return route
    except ConnectionError as e:
        logger.error(f"Connection error creating route: {e}")
        raise HTTPException(
            status_code=503, detail=f"Kong Admin API not accessible: {str(e)}"
        )
    except TimeoutError as e:
        logger.error(f"Timeout error creating route: {e}")
        raise HTTPException(status_code=504, detail=f"Kong Admin API timeout: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to create route: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/routes", response_model=List[Dict[str, Any]])
async def list_routes(
    service_name: Optional[str] = None,
    manager: KongManager = Depends(get_kong_manager),
    current_user: CasdoorUser = Depends(get_current_user),
):
    """List all Kong routes, optionally filtered by service"""
    try:
        routes = await manager.list_routes(service_name)
        return routes
    except ConnectionError as e:
        logger.error(f"Connection error listing routes: {e}")
        raise HTTPException(
            status_code=503, detail=f"Kong Admin API not accessible: {str(e)}"
        )
    except TimeoutError as e:
        logger.error(f"Timeout error listing routes: {e}")
        raise HTTPException(status_code=504, detail=f"Kong Admin API timeout: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to list routes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/routes/{route_name}", response_model=Dict[str, Any])
async def get_route(
    route_name: str,
    manager: KongManager = Depends(get_kong_manager),
    current_user: CasdoorUser = Depends(get_current_user),
):
    """Get a specific Kong route"""
    try:
        route = await manager.get_route(route_name)
        return route
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ConnectionError as e:
        logger.error(f"Connection error getting route {route_name}: {e}")
        raise HTTPException(
            status_code=503, detail=f"Kong Admin API not accessible: {str(e)}"
        )
    except TimeoutError as e:
        logger.error(f"Timeout error getting route {route_name}: {e}")
        raise HTTPException(status_code=504, detail=f"Kong Admin API timeout: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to get route {route_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/routes/{route_name}", response_model=Dict[str, Any])
async def update_route(
    route_name: str,
    request: RouteUpdateRequest,
    manager: KongManager = Depends(get_kong_manager),
    current_user: CasdoorUser = Depends(get_current_user),
):
    """Update a Kong route"""
    try:
        # Get current route to merge with updates
        current_route = await manager.get_route(route_name)

        # Create route config with merged data
        update_data = request.model_dump(exclude_none=True)
        route_config = RouteConfig(
            name=route_name,
            service_name=current_route.get("service", {}).get("name", ""),
            paths=update_data.get("paths", current_route.get("paths")),
            protocols=update_data.get("protocols", current_route.get("protocols")),
            methods=update_data.get("methods", current_route.get("methods")),
            hosts=update_data.get("hosts", current_route.get("hosts")),
            headers=update_data.get("headers", current_route.get("headers")),
            https_redirect_status_code=update_data.get(
                "https_redirect_status_code",
                current_route.get("https_redirect_status_code"),
            ),
            regex_priority=update_data.get(
                "regex_priority", current_route.get("regex_priority")
            ),
            strip_path=update_data.get("strip_path", current_route.get("strip_path")),
            preserve_host=update_data.get(
                "preserve_host", current_route.get("preserve_host")
            ),
            request_buffering=update_data.get(
                "request_buffering", current_route.get("request_buffering")
            ),
            response_buffering=update_data.get(
                "response_buffering", current_route.get("response_buffering")
            ),
            tags=update_data.get("tags", current_route.get("tags")),
        )

        route = await manager.update_route(route_name, route_config)
        return route
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ConnectionError as e:
        logger.error(f"Connection error updating route {route_name}: {e}")
        raise HTTPException(
            status_code=503, detail=f"Kong Admin API not accessible: {str(e)}"
        )
    except TimeoutError as e:
        logger.error(f"Timeout error updating route {route_name}: {e}")
        raise HTTPException(status_code=504, detail=f"Kong Admin API timeout: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to update route {route_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/routes/{route_name}", response_model=Dict[str, Any])
async def delete_route(
    route_name: str,
    manager: KongManager = Depends(get_kong_manager),
    current_user: CasdoorUser = Depends(get_current_user),
):
    """Delete a Kong route"""
    try:
        result = await manager.delete_route(route_name)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ConnectionError as e:
        logger.error(f"Connection error deleting route {route_name}: {e}")
        raise HTTPException(
            status_code=503, detail=f"Kong Admin API not accessible: {str(e)}"
        )
    except TimeoutError as e:
        logger.error(f"Timeout error deleting route {route_name}: {e}")
        raise HTTPException(status_code=504, detail=f"Kong Admin API timeout: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to delete route {route_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Plugin Management Endpoints
@router.post("/services/{service_name}/plugins", response_model=Dict[str, Any])
async def enable_plugin(
    service_name: str,
    request: PluginCreateRequest,
    manager: KongManager = Depends(get_kong_manager),
    current_user: CasdoorUser = Depends(get_current_user),
):
    """Enable a plugin on a service"""
    try:
        plugin_config = PluginConfig(**request.model_dump())
        plugin = await manager.enable_plugin(service_name, plugin_config)
        return plugin
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ConnectionError as e:
        logger.error(f"Connection error enabling plugin on service {service_name}: {e}")
        raise HTTPException(
            status_code=503, detail=f"Kong Admin API not accessible: {str(e)}"
        )
    except TimeoutError as e:
        logger.error(f"Timeout error enabling plugin on service {service_name}: {e}")
        raise HTTPException(status_code=504, detail=f"Kong Admin API timeout: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to enable plugin on service {service_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/plugins", response_model=List[Dict[str, Any]])
async def list_plugins(
    service_name: Optional[str] = None,
    manager: KongManager = Depends(get_kong_manager),
    current_user: CasdoorUser = Depends(get_current_user),
):
    """List all Kong plugins, optionally filtered by service"""
    try:
        plugins = await manager.list_plugins(service_name)
        return plugins
    except ConnectionError as e:
        logger.error(f"Connection error listing plugins: {e}")
        raise HTTPException(
            status_code=503, detail=f"Kong Admin API not accessible: {str(e)}"
        )
    except TimeoutError as e:
        logger.error(f"Timeout error listing plugins: {e}")
        raise HTTPException(status_code=504, detail=f"Kong Admin API timeout: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to list plugins: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/plugins/{plugin_id}", response_model=Dict[str, Any])
async def delete_plugin(
    plugin_id: str,
    manager: KongManager = Depends(get_kong_manager),
    current_user: CasdoorUser = Depends(get_current_user),
):
    """Delete a Kong plugin"""
    try:
        result = await manager.delete_plugin(plugin_id)
        return result
    except ConnectionError as e:
        logger.error(f"Connection error deleting plugin {plugin_id}: {e}")
        raise HTTPException(
            status_code=503, detail=f"Kong Admin API not accessible: {str(e)}"
        )
    except TimeoutError as e:
        logger.error(f"Timeout error deleting plugin {plugin_id}: {e}")
        raise HTTPException(status_code=504, detail=f"Kong Admin API timeout: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to delete plugin {plugin_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Health and Status Endpoints
@router.get("/services/{service_name}/health", response_model=ServiceHealthResponse)
async def get_service_health(
    service_name: str,
    manager: KongManager = Depends(get_kong_manager),
    current_user: CasdoorUser = Depends(get_current_user),
):
    """Get health information for a service"""
    try:
        health = await manager.get_service_health(service_name)
        return ServiceHealthResponse(**health)
    except ConnectionError as e:
        logger.error(f"Connection error getting health for service {service_name}: {e}")
        raise HTTPException(
            status_code=503, detail=f"Kong Admin API not accessible: {str(e)}"
        )
    except TimeoutError as e:
        logger.error(f"Timeout error getting health for service {service_name}: {e}")
        raise HTTPException(status_code=504, detail=f"Kong Admin API timeout: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to get health for service {service_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Complete Service Setup Endpoint
@router.post("/services/complete", response_model=Dict[str, Any])
async def setup_complete_service(
    request: CompleteServiceRequest,
    manager: KongManager = Depends(get_kong_manager),
    current_user: CasdoorUser = Depends(get_current_user),
):
    """Set up a complete service with routes and plugins"""
    try:
        service_config = ServiceConfig(**request.service.model_dump())
        route_configs = [RouteConfig(**route.model_dump()) for route in request.routes]
        plugin_configs = None

        if request.plugins:
            plugin_configs = [
                PluginConfig(**plugin.model_dump()) for plugin in request.plugins
            ]

        result = await manager.setup_complete_service(
            service_config, route_configs, plugin_configs
        )
        return result
    except ConnectionError as e:
        logger.error(f"Connection error setting up complete service: {e}")
        raise HTTPException(
            status_code=503, detail=f"Kong Admin API not accessible: {str(e)}"
        )
    except TimeoutError as e:
        logger.error(f"Timeout error setting up complete service: {e}")
        raise HTTPException(status_code=504, detail=f"Kong Admin API timeout: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to setup complete service: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Utility Endpoints
@router.get("/status")
async def kong_status(
    manager: KongManager = Depends(get_kong_manager),
    current_user: CasdoorUser = Depends(get_current_user),
):
    """Get Kong API status"""
    try:
        # Try to list services to check if Kong is accessible
        services = await manager.list_services()
        return {
            "status": "healthy",
            "kong_admin_url": manager.admin_url,
            "services_count": len(services),
        }
    except ConnectionError as e:
        logger.error(f"Kong connection error: {e}")
        return {
            "status": "unhealthy",
            "kong_admin_url": manager.admin_url,
            "error": f"Connection failed: {str(e)}",
            "error_type": "connection",
        }
    except TimeoutError as e:
        logger.error(f"Kong timeout error: {e}")
        return {
            "status": "unhealthy",
            "kong_admin_url": manager.admin_url,
            "error": f"Timeout: {str(e)}",
            "error_type": "timeout",
        }
    except Exception as e:
        logger.error(f"Kong status check failed: {e}")
        return {
            "status": "unhealthy",
            "kong_admin_url": manager.admin_url,
            "error": str(e),
            "error_type": "unknown",
        }
