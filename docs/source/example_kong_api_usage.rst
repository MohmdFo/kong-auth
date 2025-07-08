Kong Management API Examples
============================

Overview
--------

The Kong Management API comes with comprehensive examples demonstrating how to use all endpoints effectively. The example script provides practical usage patterns and best practices for managing Kong services, routes, and plugins.

Example Script
-------------

The main example script is located at: ``example_kong_api_usage.py``

This script demonstrates:

* **Service Management**: Creating, listing, updating, and deleting services
* **Route Management**: Managing routes with various configurations
* **Plugin Management**: Enabling and configuring Kong plugins
* **Complete Service Setup**: One-shot service configuration with routes and plugins
* **Error Handling**: Proper error handling and cleanup

Key Features
-----------

Client Class
^^^^^^^^^^^

The example includes a comprehensive ``KongAPIClient`` class that provides:

.. code-block:: python

   class KongAPIClient:
       """Client for interacting with the Kong Management API"""
       
       async def create_service(self, service_data: Dict[str, Any]) -> Dict[str, Any]
       async def list_services(self) -> list
       async def get_service(self, service_name: str) -> Dict[str, Any]
       async def update_service(self, service_name: str, update_data: Dict[str, Any]) -> Dict[str, Any]
       async def delete_service(self, service_name: str) -> Dict[str, Any]
       
       async def create_route(self, route_data: Dict[str, Any]) -> Dict[str, Any]
       async def list_routes(self, service_name: str = None) -> list
       async def get_route(self, route_name: str) -> Dict[str, Any]
       async def update_route(self, route_name: str, update_data: Dict[str, Any]) -> Dict[str, Any]
       async def delete_route(self, route_name: str) -> Dict[str, Any]
       
       async def enable_plugin(self, service_name: str, plugin_data: Dict[str, Any]) -> Dict[str, Any]
       async def list_plugins(self, service_name: str = None) -> list
       
       async def get_service_health(self, service_name: str) -> Dict[str, Any]
       async def get_kong_status(self) -> Dict[str, Any]
       async def setup_complete_service(self, complete_service_data: Dict[str, Any]) -> Dict[str, Any]

Example Categories
-----------------

Basic Service Management
^^^^^^^^^^^^^^^^^^^^^^^

Demonstrates fundamental service operations:

.. code-block:: python

   # Create a simple service
   service_data = {
       "name": "example-service",
       "url": "http://localhost:8001",
       "protocol": "http",
       "tags": ["example", "test"]
   }
   
   service = await client.create_service(service_data)
   services = await client.list_services()
   service_details = await client.get_service("example-service")

Route Management
^^^^^^^^^^^^^^^

Shows how to create and manage routes:

.. code-block:: python

   # Create routes for a service
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
       }
   ]

Plugin Management
^^^^^^^^^^^^^^^^

Demonstrates plugin configuration:

.. code-block:: python

   # Enable JWT plugin
   jwt_plugin_data = {
       "name": "jwt",
       "config": {
           "uri_param_names": ["jwt"],
           "key_claim_name": "iss",
           "secret_is_base64": True,
           "claims_to_verify": ["exp"],
           "header_names": ["authorization"]
       },
       "enabled": True,
       "tags": ["security", "jwt"]
   }
   
   # Enable CORS plugin
   cors_plugin_data = {
       "name": "cors",
       "config": {
           "origins": ["*"],
           "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
           "headers": ["Content-Type", "Authorization"],
           "credentials": True
       },
       "enabled": True,
       "tags": ["cors", "security"]
   }

Complete Service Setup
^^^^^^^^^^^^^^^^^^^^^

Shows one-shot service configuration:

.. code-block:: python

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
           }
       ]
   }

Running the Examples
-------------------

Prerequisites
^^^^^^^^^^^^

1. **Kong Gateway**: Must be running and accessible
2. **API Server**: Your Kong Auth Service must be running
3. **Python Dependencies**: Install required packages

Setup
^^^^^

.. code-block:: bash

   # Start Kong for testing
   ./start-kong-for-testing.sh
   
   # Or manually start Kong
   docker-compose -f kong/docker-compose.kong.yml up -d
   
   # Start the API server
   python -m app.main

Execution
^^^^^^^^^

.. code-block:: bash

   # Run all examples
   python example_kong_api_usage.py
   
   # Run specific examples (modify the script)
   # Comment out unwanted examples in the main() function

Output
^^^^^^

The script provides detailed output showing:

* ✅ Success messages with created resources
* 📋 Lists of services, routes, and plugins
* 🔄 Update operations and their results
* 🏥 Health check information
* 🧹 Cleanup operations

Example Output
-------------

.. code-block:: text

   🎯 Kong Management API Examples
   ================================================================
   API Base URL: http://localhost:8000
   Kong Admin URL: http://localhost:8006
   ================================================================

   🔧 Basic Service Management Example
   ==================================================
   Kong Status: {'status': 'healthy', 'kong_admin_url': 'http://localhost:8006', 'services_count': 0}

   📝 Creating service: example-service
   ✅ Service created: {'id': 'uuid', 'name': 'example-service', 'url': 'http://localhost:8001', ...}

   📋 Listing all services:
     - example-service: http://localhost:8001

   🔍 Getting service details:
   Service details: {'id': 'uuid', 'name': 'example-service', ...}

   🔄 Updating service:
   ✅ Service updated: {'id': 'uuid', 'name': 'example-service', ...}

Error Handling
-------------

The examples demonstrate proper error handling:

* **Connection Errors**: When Kong is not accessible
* **Validation Errors**: When request data is invalid
* **Resource Conflicts**: When services/routes already exist
* **Not Found Errors**: When resources don't exist

Best Practices
-------------

1. **Async Context Manager**: Use the client as an async context manager for proper resource cleanup
2. **Error Handling**: Always handle potential exceptions
3. **Resource Cleanup**: Clean up test resources after use
4. **Validation**: Validate responses and handle edge cases
5. **Logging**: Use appropriate logging for debugging

Customization
------------

You can customize the examples by:

* **Modifying Configuration**: Change URLs, timeouts, and other settings
* **Adding New Examples**: Create additional test scenarios
* **Extending the Client**: Add new methods to the KongAPIClient class
* **Integration Testing**: Use the examples as a foundation for integration tests

Integration with Your Application
--------------------------------

The examples can be adapted for your application by:

1. **Importing the Client**: Use KongAPIClient in your application code
2. **Configuration Management**: Load settings from environment variables or config files
3. **Error Handling**: Implement application-specific error handling
4. **Logging**: Integrate with your application's logging system
5. **Testing**: Use the examples as a basis for your test suite

See Also
--------

* :doc:`kong-management-api` - Complete API reference
* :doc:`../README` - Project overview and setup instructions
* :doc:`test_kong_api` - Automated test suite 