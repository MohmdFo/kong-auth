Kong Management API
==================

Overview
--------

The Kong Management API provides a complete REST interface for managing Kong services, routes, and plugins through your main application. This API allows users to define their own services and paths without directly accessing Kong's Admin API.

Base URL: ``http://localhost:8000/kong``

.. note::
   All endpoints return JSON responses and use standard HTTP status codes.

Service Management
-----------------

Create Service
~~~~~~~~~~~~~

**Endpoint:** ``POST /kong/services``

Creates a new Kong service.

**Request Body:**

.. code-block:: json

   {
     "name": "my-service",
     "url": "http://localhost:8001",
     "protocol": "http",
     "host": "localhost",
     "port": 8001,
     "path": "/",
     "retries": 5,
     "connect_timeout": 60000,
     "write_timeout": 60000,
     "read_timeout": 60000,
     "tags": ["production", "api"]
   }

**Parameters:**

* **name** (string, required): Unique identifier for the service. Must be alphanumeric with hyphens and underscores allowed.
* **url** (string, required): The upstream service URL. Must start with ``http://`` or ``https://``.
* **protocol** (string, optional): The protocol used to communicate with the upstream. Default: ``http``. Valid values: ``http``, ``https``, ``tcp``, ``tls``.
* **host** (string, optional): The host of the upstream server. If not provided, extracted from URL.
* **port** (integer, optional): The port on which the upstream server is listening. If not provided, extracted from URL.
* **path** (string, optional): The path to be used when calling the upstream service. Default: ``/``.
* **retries** (integer, optional): Number of retries to execute upon failure. Default: 5.
* **connect_timeout** (integer, optional): The timeout in milliseconds for establishing a connection to the upstream server. Default: 60000.
* **write_timeout** (integer, optional): The timeout in milliseconds for transmitting data to the upstream server. Default: 60000.
* **read_timeout** (integer, optional): The timeout in milliseconds for receiving data from the upstream server. Default: 60000.
* **tags** (array of strings, optional): An optional set of strings associated with the service for grouping and filtering.

**Response:**

.. code-block:: json

   {
     "id": "uuid",
     "name": "my-service",
     "url": "http://localhost:8001",
     "protocol": "http",
     "host": "localhost",
     "port": 8001,
     "path": "/",
     "retries": 5,
     "connect_timeout": 60000,
     "write_timeout": 60000,
     "read_timeout": 60000,
     "tags": ["production", "api"],
     "created_at": 1234567890
   }

**Status Codes:**

* ``200 OK``: Service created successfully
* ``409 Conflict``: Service already exists (returns existing service)
* ``400 Bad Request``: Invalid request data
* ``503 Service Unavailable``: Kong Admin API not accessible
* ``500 Internal Server Error``: Server error

List Services
~~~~~~~~~~~~

**Endpoint:** ``GET /kong/services``

Returns all Kong services.

**Response:**

.. code-block:: json

   [
     {
       "id": "uuid",
       "name": "my-service",
       "url": "http://localhost:8001",
       "protocol": "http",
       "created_at": 1234567890
     }
   ]

**Status Codes:**

* ``200 OK``: Services retrieved successfully
* ``503 Service Unavailable``: Kong Admin API not accessible
* ``500 Internal Server Error``: Server error

Get Service
~~~~~~~~~~

**Endpoint:** ``GET /kong/services/{service_name}``

Returns a specific Kong service.

**Path Parameters:**

* **service_name** (string, required): The name of the service to retrieve.

**Response:**

.. code-block:: json

   {
     "id": "uuid",
     "name": "my-service",
     "url": "http://localhost:8001",
     "protocol": "http",
     "host": "localhost",
     "port": 8001,
     "path": "/",
     "retries": 5,
     "connect_timeout": 60000,
     "write_timeout": 60000,
     "read_timeout": 60000,
     "tags": ["production", "api"],
     "created_at": 1234567890
   }

**Status Codes:**

* ``200 OK``: Service retrieved successfully
* ``404 Not Found``: Service not found
* ``503 Service Unavailable``: Kong Admin API not accessible
* ``500 Internal Server Error``: Server error

Update Service
~~~~~~~~~~~~~

**Endpoint:** ``PATCH /kong/services/{service_name}``

Updates an existing Kong service.

**Path Parameters:**

* **service_name** (string, required): The name of the service to update.

**Request Body:**

.. code-block:: json

   {
     "url": "http://localhost:8002",
     "connect_timeout": 30000,
     "tags": ["staging", "api"]
   }

**Parameters:**

* **url** (string, optional): The upstream service URL. Must start with ``http://`` or ``https://``.
* **protocol** (string, optional): The protocol used to communicate with the upstream. Valid values: ``http``, ``https``, ``tcp``, ``tls``.
* **host** (string, optional): The host of the upstream server.
* **port** (integer, optional): The port on which the upstream server is listening.
* **path** (string, optional): The path to be used when calling the upstream service.
* **retries** (integer, optional): Number of retries to execute upon failure.
* **connect_timeout** (integer, optional): The timeout in milliseconds for establishing a connection.
* **write_timeout** (integer, optional): The timeout in milliseconds for transmitting data.
* **read_timeout** (integer, optional): The timeout in milliseconds for receiving data.
* **tags** (array of strings, optional): An optional set of strings for grouping and filtering.

**Response:**

.. code-block:: json

   {
     "id": "uuid",
     "name": "my-service",
     "url": "http://localhost:8002",
     "protocol": "http",
     "connect_timeout": 30000,
     "tags": ["staging", "api"],
     "updated_at": 1234567890
   }

**Status Codes:**

* ``200 OK``: Service updated successfully
* ``404 Not Found``: Service not found
* ``400 Bad Request``: Invalid request data
* ``503 Service Unavailable``: Kong Admin API not accessible
* ``500 Internal Server Error``: Server error

Delete Service
~~~~~~~~~~~~~

**Endpoint:** ``DELETE /kong/services/{service_name}``

Deletes a Kong service.

**Path Parameters:**

* **service_name** (string, required): The name of the service to delete.

**Response:**

.. code-block:: json

   {
     "message": "Service 'my-service' deleted successfully"
   }

**Status Codes:**

* ``200 OK``: Service deleted successfully
* ``404 Not Found``: Service not found
* ``503 Service Unavailable``: Kong Admin API not accessible
* ``500 Internal Server Error``: Server error

Route Management
---------------

Create Route
~~~~~~~~~~~

**Endpoint:** ``POST /kong/routes``

Creates a new Kong route.

**Request Body:**

.. code-block:: json

   {
     "name": "my-route",
     "service_name": "my-service",
     "paths": ["/api/v1"],
     "protocols": ["http", "https"],
     "methods": ["GET", "POST", "PUT", "DELETE"],
     "hosts": ["api.example.com"],
     "headers": {
       "x-api-version": ["v1"]
     },
     "https_redirect_status_code": 426,
     "regex_priority": 0,
     "strip_path": true,
     "preserve_host": false,
     "request_buffering": true,
     "response_buffering": true,
     "tags": ["api", "v1"]
   }

**Parameters:**

* **name** (string, required): Unique identifier for the route. Must be alphanumeric with hyphens and underscores allowed.
* **service_name** (string, required): The name of the service this route belongs to.
* **paths** (array of strings, optional): A list of paths that match this route. At least one of ``hosts``, ``paths``, or ``methods`` must be set.
* **protocols** (array of strings, optional): A list of protocols this route should allow. Default: ``["http", "https"]``. Valid values: ``http``, ``https``, ``grpc``, ``grpcs``, ``tcp``, ``tls``.
* **methods** (array of strings, optional): A list of HTTP methods this route should allow. Valid values: ``GET``, ``POST``, ``PUT``, ``PATCH``, ``DELETE``, ``HEAD``, ``OPTIONS``, ``TRACE``, ``CONNECT``.
* **hosts** (array of strings, optional): A list of domain names that match this route. At least one of ``hosts``, ``paths``, or ``methods`` must be set.
* **headers** (object, optional): A list of headers that match this route. Keys are header names, values are arrays of header values.
* **https_redirect_status_code** (integer, optional): The status code Kong responds with when all properties of a route except ``protocols`` are the same. Default: 426. Valid values: 301, 302, 307, 308, 426.
* **regex_priority** (integer, optional): A number used to choose which route resolves a given request when several routes match it using regexes simultaneously. Default: 0.
* **strip_path** (boolean, optional): When matching a route via one of the ``paths``, strip the matched prefix from the upstream request URL. Default: true.
* **preserve_host** (boolean, optional): When matching a route via one of the ``hosts`` domain names, use the request header as the upstream request header. Default: false.
* **request_buffering** (boolean, optional): Whether to enable request body buffering. Default: true.
* **response_buffering** (boolean, optional): Whether to enable response body buffering. Default: true.
* **tags** (array of strings, optional): An optional set of strings associated with the route for grouping and filtering.

**Response:**

.. code-block:: json

   {
     "id": "uuid",
     "name": "my-route",
     "service": {
       "id": "service-uuid",
       "name": "my-service"
     },
     "paths": ["/api/v1"],
     "protocols": ["http", "https"],
     "methods": ["GET", "POST", "PUT", "DELETE"],
     "hosts": ["api.example.com"],
     "headers": {
       "x-api-version": ["v1"]
     },
     "https_redirect_status_code": 426,
     "regex_priority": 0,
     "strip_path": true,
     "preserve_host": false,
     "request_buffering": true,
     "response_buffering": true,
     "tags": ["api", "v1"],
     "created_at": 1234567890
   }

**Status Codes:**

* ``200 OK``: Route created successfully
* ``409 Conflict``: Route already exists (returns existing route)
* ``400 Bad Request``: Invalid request data
* ``503 Service Unavailable``: Kong Admin API not accessible
* ``500 Internal Server Error``: Server error

List Routes
~~~~~~~~~~

**Endpoint:** ``GET /kong/routes``

Returns all Kong routes.

**Query Parameters:**

* **service_name** (string, optional): Filter routes by service name.

**Response:**

.. code-block:: json

   [
     {
       "id": "uuid",
       "name": "my-route",
       "service": {
         "id": "service-uuid",
         "name": "my-service"
       },
       "paths": ["/api/v1"],
       "protocols": ["http", "https"],
       "methods": ["GET", "POST", "PUT", "DELETE"],
       "created_at": 1234567890
     }
   ]

**Status Codes:**

* ``200 OK``: Routes retrieved successfully
* ``503 Service Unavailable``: Kong Admin API not accessible
* ``500 Internal Server Error``: Server error

Get Route
~~~~~~~~~

**Endpoint:** ``GET /kong/routes/{route_name}``

Returns a specific Kong route.

**Path Parameters:**

* **route_name** (string, required): The name of the route to retrieve.

**Response:**

.. code-block:: json

   {
     "id": "uuid",
     "name": "my-route",
     "service": {
       "id": "service-uuid",
       "name": "my-service"
     },
     "paths": ["/api/v1"],
     "protocols": ["http", "https"],
     "methods": ["GET", "POST", "PUT", "DELETE"],
     "hosts": ["api.example.com"],
     "headers": {
       "x-api-version": ["v1"]
     },
     "https_redirect_status_code": 426,
     "regex_priority": 0,
     "strip_path": true,
     "preserve_host": false,
     "request_buffering": true,
     "response_buffering": true,
     "tags": ["api", "v1"],
     "created_at": 1234567890
   }

**Status Codes:**

* ``200 OK``: Route retrieved successfully
* ``404 Not Found``: Route not found
* ``503 Service Unavailable``: Kong Admin API not accessible
* ``500 Internal Server Error``: Server error

Update Route
~~~~~~~~~~~

**Endpoint:** ``PATCH /kong/routes/{route_name}``

Updates an existing Kong route.

**Path Parameters:**

* **route_name** (string, required): The name of the route to update.

**Request Body:**

.. code-block:: json

   {
     "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     "strip_path": false,
     "tags": ["api", "v1", "updated"]
   }

**Parameters:**

* **paths** (array of strings, optional): A list of paths that match this route.
* **protocols** (array of strings, optional): A list of protocols this route should allow.
* **methods** (array of strings, optional): A list of HTTP methods this route should allow.
* **hosts** (array of strings, optional): A list of domain names that match this route.
* **headers** (object, optional): A list of headers that match this route.
* **https_redirect_status_code** (integer, optional): The status code for HTTPS redirects.
* **regex_priority** (integer, optional): Priority for regex matching.
* **strip_path** (boolean, optional): Whether to strip the matched path prefix.
* **preserve_host** (boolean, optional): Whether to preserve the host header.
* **request_buffering** (boolean, optional): Whether to enable request buffering.
* **response_buffering** (boolean, optional): Whether to enable response buffering.
* **tags** (array of strings, optional): An optional set of strings for grouping and filtering.

**Response:**

.. code-block:: json

   {
     "id": "uuid",
     "name": "my-route",
     "service": {
       "id": "service-uuid",
       "name": "my-service"
     },
     "paths": ["/api/v1"],
     "protocols": ["http", "https"],
     "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     "strip_path": false,
     "tags": ["api", "v1", "updated"],
     "updated_at": 1234567890
   }

**Status Codes:**

* ``200 OK``: Route updated successfully
* ``404 Not Found``: Route not found
* ``400 Bad Request``: Invalid request data
* ``503 Service Unavailable``: Kong Admin API not accessible
* ``500 Internal Server Error``: Server error

Delete Route
~~~~~~~~~~~

**Endpoint:** ``DELETE /kong/routes/{route_name}``

Deletes a Kong route.

**Path Parameters:**

* **route_name** (string, required): The name of the route to delete.

**Response:**

.. code-block:: json

   {
     "message": "Route 'my-route' deleted successfully"
   }

**Status Codes:**

* ``200 OK``: Route deleted successfully
* ``404 Not Found``: Route not found
* ``503 Service Unavailable``: Kong Admin API not accessible
* ``500 Internal Server Error``: Server error

Plugin Management
----------------

Enable Plugin
~~~~~~~~~~~~

**Endpoint:** ``POST /kong/services/{service_name}/plugins``

Enables a plugin on a service.

**Path Parameters:**

* **service_name** (string, required): The name of the service to enable the plugin on.

**Request Body:**

.. code-block:: json

   {
     "name": "jwt",
     "config": {
       "uri_param_names": ["jwt"],
       "cookie_names": ["jwt"],
       "key_claim_name": "iss",
       "secret_is_base64": true,
       "claims_to_verify": ["exp"],
       "anonymous": null,
       "run_on_preflight": true,
       "maximum_expiration": 31536000,
       "header_names": ["authorization"]
     },
     "enabled": true,
     "tags": ["security", "jwt"]
   }

**Parameters:**

* **name** (string, required): The name of the plugin to enable. Valid values depend on Kong plugins installed.
* **config** (object, required): Plugin-specific configuration. Structure varies by plugin type.
* **enabled** (boolean, optional): Whether the plugin is enabled. Default: true.
* **tags** (array of strings, optional): An optional set of strings associated with the plugin.

**Common Plugin Configurations:**

**JWT Plugin:**
.. code-block:: json

   {
     "uri_param_names": ["jwt"],
     "cookie_names": ["jwt"],
     "key_claim_name": "iss",
     "secret_is_base64": true,
     "claims_to_verify": ["exp"],
     "anonymous": null,
     "run_on_preflight": true,
     "maximum_expiration": 31536000,
     "header_names": ["authorization"]
   }

**CORS Plugin:**
.. code-block:: json

   {
     "origins": ["*"],
     "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     "headers": ["Content-Type", "Authorization"],
     "exposed_headers": ["X-Consumer-ID"],
     "credentials": true,
     "max_age": 3600,
     "preflight_continue": false
   }

**Rate Limiting Plugin:**
.. code-block:: json

   {
     "minute": 100,
     "hour": 1000,
     "policy": "local"
   }

**Response:**

.. code-block:: json

   {
     "id": "uuid",
     "name": "jwt",
     "service": {
       "id": "service-uuid",
       "name": "my-service"
     },
     "config": {
       "uri_param_names": ["jwt"],
       "cookie_names": ["jwt"],
       "key_claim_name": "iss",
       "secret_is_base64": true,
       "claims_to_verify": ["exp"],
       "anonymous": null,
       "run_on_preflight": true,
       "maximum_expiration": 31536000,
       "header_names": ["authorization"]
     },
     "enabled": true,
     "tags": ["security", "jwt"],
     "created_at": 1234567890
   }

**Status Codes:**

* ``200 OK``: Plugin enabled successfully
* ``409 Conflict``: Plugin already enabled (returns existing plugin)
* ``404 Not Found``: Service not found
* ``400 Bad Request``: Invalid request data
* ``503 Service Unavailable``: Kong Admin API not accessible
* ``500 Internal Server Error``: Server error

List Plugins
~~~~~~~~~~~

**Endpoint:** ``GET /kong/plugins``

Returns all Kong plugins.

**Query Parameters:**

* **service_name** (string, optional): Filter plugins by service name.

**Response:**

.. code-block:: json

   [
     {
       "id": "uuid",
       "name": "jwt",
       "service": {
         "id": "service-uuid",
         "name": "my-service"
       },
       "config": {
         "uri_param_names": ["jwt"],
         "key_claim_name": "iss",
         "secret_is_base64": true,
         "claims_to_verify": ["exp"],
         "header_names": ["authorization"]
       },
       "enabled": true,
       "tags": ["security", "jwt"],
       "created_at": 1234567890
     }
   ]

**Status Codes:**

* ``200 OK``: Plugins retrieved successfully
* ``503 Service Unavailable``: Kong Admin API not accessible
* ``500 Internal Server Error``: Server error

Delete Plugin
~~~~~~~~~~~~

**Endpoint:** ``DELETE /kong/plugins/{plugin_id}``

Deletes a Kong plugin.

**Path Parameters:**

* **plugin_id** (string, required): The ID of the plugin to delete.

**Response:**

.. code-block:: json

   {
     "message": "Plugin 'uuid' deleted successfully"
   }

**Status Codes:**

* ``200 OK``: Plugin deleted successfully
* ``404 Not Found``: Plugin not found
* ``503 Service Unavailable``: Kong Admin API not accessible
* ``500 Internal Server Error``: Server error

Health and Monitoring
--------------------

Get Service Health
~~~~~~~~~~~~~~~~~

**Endpoint:** ``GET /kong/services/{service_name}/health``

Returns health information for a service.

**Path Parameters:**

* **service_name** (string, required): The name of the service to check health for.

**Response:**

.. code-block:: json

   {
     "service": {
       "id": "uuid",
       "name": "my-service",
       "url": "http://localhost:8001",
       "protocol": "http",
       "created_at": 1234567890
     },
     "routes": [
       {
         "id": "route-uuid",
         "name": "my-route",
         "paths": ["/api/v1"],
         "methods": ["GET", "POST", "PUT", "DELETE"]
       }
     ],
     "plugins": [
       {
         "id": "plugin-uuid",
         "name": "jwt",
         "enabled": true
       }
     ],
     "status": "healthy"
   }

**Response Fields:**

* **service** (object): The service details.
* **routes** (array): List of routes associated with the service.
* **plugins** (array): List of plugins enabled on the service.
* **status** (string): Health status. Values: ``healthy``, ``unhealthy``, ``error``.
* **error** (string, optional): Error message if status is ``error``.

**Status Codes:**

* ``200 OK``: Health information retrieved successfully
* ``503 Service Unavailable``: Kong Admin API not accessible
* ``500 Internal Server Error``: Server error

Get Kong Status
~~~~~~~~~~~~~~

**Endpoint:** ``GET /kong/status``

Returns Kong API status.

**Response:**

.. code-block:: json

   {
     "status": "healthy",
     "kong_admin_url": "http://localhost:8006",
     "services_count": 5
   }

**Response Fields:**

* **status** (string): Kong status. Values: ``healthy``, ``unhealthy``.
* **kong_admin_url** (string): The Kong Admin API URL.
* **services_count** (integer): Number of services in Kong (only if healthy).
* **error** (string, optional): Error message if status is ``unhealthy``.
* **error_type** (string, optional): Type of error. Values: ``connection``, ``timeout``, ``unknown``.

**Status Codes:**

* ``200 OK``: Status retrieved successfully

Complete Service Setup
---------------------

Setup Complete Service
~~~~~~~~~~~~~~~~~~~~~

**Endpoint:** ``POST /kong/services/complete``

Sets up a complete service with routes and plugins in one request.

**Request Body:**

.. code-block:: json

   {
     "service": {
       "name": "complete-service",
       "url": "http://localhost:8001",
       "protocol": "http",
       "connect_timeout": 60000,
       "write_timeout": 60000,
       "read_timeout": 60000,
       "tags": ["production", "api"]
     },
     "routes": [
       {
         "name": "complete-service-main",
         "service_name": "complete-service",
         "paths": ["/api"],
         "methods": ["GET", "POST", "OPTIONS"],
         "strip_path": true,
         "tags": ["main"]
       },
       {
         "name": "complete-service-admin",
         "service_name": "complete-service",
         "paths": ["/api/admin"],
         "methods": ["GET", "POST", "PUT", "DELETE"],
         "strip_path": true,
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
         "enabled": true,
         "tags": ["rate-limiting"]
       },
       {
         "name": "cors",
         "config": {
           "origins": ["*"],
           "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
           "headers": ["Content-Type", "Authorization"],
           "credentials": true
         },
         "enabled": true,
         "tags": ["cors"]
       }
     ]
   }

**Parameters:**

* **service** (object, required): Service configuration. See `Create Service`_ for parameters.
* **routes** (array, required): List of route configurations. See `Create Route`_ for parameters.
* **plugins** (array, optional): List of plugin configurations. See `Enable Plugin`_ for parameters.

**Response:**

.. code-block:: json

   {
     "service": {
       "id": "uuid",
       "name": "complete-service",
       "url": "http://localhost:8001",
       "protocol": "http",
       "created_at": 1234567890
     },
     "routes": [
       {
         "id": "route-uuid-1",
         "name": "complete-service-main",
         "paths": ["/api"],
         "methods": ["GET", "POST", "OPTIONS"]
       },
       {
         "id": "route-uuid-2",
         "name": "complete-service-admin",
         "paths": ["/api/admin"],
         "methods": ["GET", "POST", "PUT", "DELETE"]
       }
     ],
     "plugins": [
       {
         "id": "plugin-uuid-1",
         "name": "rate-limiting",
         "enabled": true
       },
       {
         "id": "plugin-uuid-2",
         "name": "cors",
         "enabled": true
       }
     ],
     "status": "success"
   }

**Status Codes:**

* ``200 OK``: Complete service setup successful
* ``400 Bad Request``: Invalid request data
* ``503 Service Unavailable``: Kong Admin API not accessible
* ``500 Internal Server Error``: Server error

Error Handling
-------------

All endpoints return standard HTTP status codes and error responses in the following format:

.. code-block:: json

   {
     "detail": "Error message describing what went wrong"
   }

**Common Status Codes:**

* ``200 OK``: Request successful
* ``201 Created``: Resource created successfully
* ``400 Bad Request``: Invalid request data
* ``404 Not Found``: Resource not found
* ``409 Conflict``: Resource already exists
* ``503 Service Unavailable``: Kong Admin API not accessible
* ``504 Gateway Timeout``: Kong Admin API timeout
* ``500 Internal Server Error``: Server error

**Error Types:**

* **Connection Errors (503)**: Kong Admin API is not accessible. Check if Kong is running.
* **Timeout Errors (504)**: Kong Admin API is slow to respond or overloaded.
* **Validation Errors (400)**: Request data is invalid or missing required fields.
* **Not Found Errors (404)**: The requested resource doesn't exist.
* **Conflict Errors (409)**: The resource already exists (for creation endpoints).

Usage Examples
-------------

Using curl
~~~~~~~~~

**Create a service:**

.. code-block:: bash

   curl -X POST http://localhost:8000/kong/services \
     -H "Content-Type: application/json" \
     -d '{
       "name": "my-api",
       "url": "http://localhost:3000",
       "protocol": "http",
       "tags": ["production"]
     }'

**Create a route:**

.. code-block:: bash

   curl -X POST http://localhost:8000/kong/routes \
     -H "Content-Type: application/json" \
     -d '{
       "name": "my-api-route",
       "service_name": "my-api",
       "paths": ["/api/v1"],
       "methods": ["GET", "POST", "PUT", "DELETE"],
       "strip_path": true
     }'

**Enable JWT plugin:**

.. code-block:: bash

   curl -X POST http://localhost:8000/kong/services/my-api/plugins \
     -H "Content-Type: application/json" \
     -d '{
       "name": "jwt",
       "config": {
         "uri_param_names": ["jwt"],
         "key_claim_name": "iss",
         "secret_is_base64": true,
         "claims_to_verify": ["exp"],
         "header_names": ["authorization"]
       },
       "enabled": true
     }'

**Complete service setup:**

.. code-block:: bash

   curl -X POST http://localhost:8000/kong/services/complete \
     -H "Content-Type: application/json" \
     -d '{
       "service": {
         "name": "my-api",
         "url": "http://localhost:3000",
         "protocol": "http"
       },
       "routes": [
         {
           "name": "my-api-route",
           "service_name": "my-api",
           "paths": ["/api/v1"],
           "methods": ["GET", "POST", "PUT", "DELETE"]
         }
       ],
       "plugins": [
         {
           "name": "cors",
           "config": {
             "origins": ["*"],
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
             "headers": ["Content-Type", "Authorization"]
           }
         }
       ]
     }'

Using Python
~~~~~~~~~~~

See :doc:`../example_kong_api_usage` for comprehensive Python examples.

Best Practices
-------------

1. **Service Naming**: Use descriptive, unique names for services (e.g., ``user-service``, ``payment-api``)
2. **Route Paths**: Use versioned paths (e.g., ``/api/v1``, ``/api/v2``) for API versioning
3. **Tags**: Use tags to organize and categorize services, routes, and plugins
4. **Error Handling**: Always handle potential errors in your client code
5. **Health Checks**: Regularly check service health using the health endpoint
6. **Cleanup**: Remove unused services and routes to keep Kong clean
7. **Security**: Use appropriate plugins (JWT, CORS, Rate Limiting) for production services

Configuration
------------

The API uses the following environment variables:

* **KONG_ADMIN_URL**: Kong Admin API URL (default: ``http://localhost:8006``)
* **API_BASE_URL**: Your API base URL (default: ``http://localhost:8000``)

Security Considerations
---------------------

1. **Authentication**: Implement proper authentication for production use
2. **Authorization**: Add role-based access control
3. **Rate Limiting**: Consider implementing rate limiting on the API
4. **Input Validation**: All inputs are validated using Pydantic models
5. **HTTPS**: Use HTTPS in production environments
6. **CORS**: Configure CORS appropriately for your use case

Troubleshooting
--------------

**Common Issues:**

1. **Service already exists**: Use PATCH to update instead of POST to create
2. **Route not found**: Ensure the service exists before creating routes
3. **Plugin configuration errors**: Check Kong plugin documentation for valid config options
4. **Connection errors**: Verify Kong Admin API is accessible

**Debugging:**

1. Check Kong status: ``GET /kong/status``
2. Check service health: ``GET /kong/services/{service_name}/health``
3. Review application logs for detailed error messages
4. Verify Kong Admin API connectivity: ``curl http://localhost:8006/status``

Migration from setup-kong.py
---------------------------

If you're migrating from the static ``setup-kong.py`` script:

1. Replace static service definitions with API calls
2. Use the complete service setup endpoint for complex configurations
3. Implement dynamic service management based on your application needs
4. Add proper error handling and retry logic 