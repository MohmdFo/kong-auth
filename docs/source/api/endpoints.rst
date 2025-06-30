API Endpoints Reference
=======================

Complete documentation of all available API endpoints in Kong Auth Service.

Overview
--------

The Kong Auth Service provides a REST API for managing users and JWT tokens. All endpoints return JSON responses and use standard HTTP status codes.

Base URLs
---------

* **Auth Service**: `http://localhost:8000` (development)
* **Kong Gateway**: `http://localhost:8005` (protected endpoints)
* **Sample Service**: `http://localhost:8001` (direct access)

Authentication
--------------

Most endpoints require JWT authentication. Include your JWT token in the Authorization header:

.. code-block:: bash

   Authorization: Bearer YOUR_JWT_TOKEN

Auth Service Endpoints
---------------------

These endpoints are provided by the Auth Service and don't require authentication.

Create Consumer
^^^^^^^^^^^^^^

Creates a new user (consumer) in Kong and generates a JWT token.

**Endpoint**: `POST /create-consumer`

**Request Body**:

.. code-block:: json

   {
     "username": "string",
     "custom_id": "string (optional)"
   }

**Response**:

.. code-block:: json

   {
     "consumer_id": "uuid",
     "username": "string",
     "jwt_token": "string",
     "secret": "string"
   }

**Example**:

.. code-block:: bash

   curl -X POST "http://localhost:8000/create-consumer" \
     -H "Content-Type: application/json" \
     -d '{"username": "john_doe"}'

**Status Codes**:
- `201 Created` - Consumer created successfully
- `400 Bad Request` - Invalid request data
- `409 Conflict` - Username already exists
- `500 Internal Server Error` - Server error

Generate Token
^^^^^^^^^^^^^

Generates a new JWT token for an existing consumer.

**Endpoint**: `POST /generate-token`

**Request Body**:

.. code-block:: json

   {
     "username": "string"
   }

**Response**:

.. code-block:: json

   {
     "jwt_token": "string",
     "expires_at": "timestamp"
   }

**Example**:

.. code-block:: bash

   curl -X POST "http://localhost:8000/generate-token" \
     -H "Content-Type: application/json" \
     -d '{"username": "john_doe"}'

**Status Codes**:
- `200 OK` - Token generated successfully
- `404 Not Found` - Consumer not found
- `500 Internal Server Error` - Server error

List Consumers
^^^^^^^^^^^^^

Lists all consumers in Kong.

**Endpoint**: `GET /consumers`

**Response**:

.. code-block:: json

   {
     "consumers": [
       {
         "id": "uuid",
         "username": "string",
         "created_at": "timestamp"
       }
     ]
   }

**Example**:

.. code-block:: bash

   curl "http://localhost:8000/consumers"

**Status Codes**:
- `200 OK` - Consumers retrieved successfully
- `500 Internal Server Error` - Server error

Get Consumer
^^^^^^^^^^^

Gets information about a specific consumer.

**Endpoint**: `GET /consumers/{username}`

**Response**:

.. code-block:: json

   {
     "id": "uuid",
     "username": "string",
     "created_at": "timestamp"
   }

**Example**:

.. code-block:: bash

   curl "http://localhost:8000/consumers/john_doe"

**Status Codes**:
- `200 OK` - Consumer found
- `404 Not Found` - Consumer not found
- `500 Internal Server Error` - Server error

Delete Consumer
^^^^^^^^^^^^^^

Deletes a consumer and all associated credentials.

**Endpoint**: `DELETE /consumers/{username}`

**Response**:

.. code-block:: json

   {
     "message": "Consumer deleted successfully"
   }

**Example**:

.. code-block:: bash

   curl -X DELETE "http://localhost:8000/consumers/john_doe"

**Status Codes**:
- `200 OK` - Consumer deleted successfully
- `404 Not Found` - Consumer not found
- `500 Internal Server Error` - Server error

Health Check
^^^^^^^^^^^

Checks the health of the Auth Service.

**Endpoint**: `GET /health`

**Response**:

.. code-block:: json

   {
     "status": "healthy",
     "timestamp": "timestamp",
     "version": "string"
   }

**Example**:

.. code-block:: bash

   curl "http://localhost:8000/health"

**Status Codes**:
- `200 OK` - Service is healthy
- `503 Service Unavailable` - Service is unhealthy

Sample Service Endpoints
-----------------------

These endpoints are provided by the Sample Service and require JWT authentication.

Service Status
^^^^^^^^^^^^^

Gets the current status of the sample service.

**Endpoint**: `GET /sample/status`

**Headers Required**:

.. code-block:: bash

   Authorization: Bearer YOUR_JWT_TOKEN

**Response**:

.. code-block:: json

   {
     "status": "ok",
     "message": "Sample service is running",
     "user": "string",
     "timestamp": "timestamp"
   }

**Example**:

.. code-block:: bash

   curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     "http://localhost:8005/sample/status"

**Status Codes**:
- `200 OK` - Service is running
- `401 Unauthorized` - Invalid or missing JWT token
- `500 Internal Server Error` - Service error

User Information
^^^^^^^^^^^^^^^^

Gets information about the authenticated user.

**Endpoint**: `GET /sample/user-info`

**Headers Required**:

.. code-block:: bash

   Authorization: Bearer YOUR_JWT_TOKEN

**Response**:

.. code-block:: json

   {
     "user_id": "string",
     "username": "string",
     "authenticated_at": "timestamp",
     "token_info": {
       "issuer": "string",
       "expires_at": "timestamp",
       "issued_at": "timestamp"
     }
   }

**Example**:

.. code-block:: bash

   curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     "http://localhost:8005/sample/user-info"

**Status Codes**:
- `200 OK` - User information retrieved
- `401 Unauthorized` - Invalid or missing JWT token
- `500 Internal Server Error` - Service error

Protected Data
^^^^^^^^^^^^^

Gets sample data that requires authentication.

**Endpoint**: `GET /sample/data`

**Headers Required**:

.. code-block:: bash

   Authorization: Bearer YOUR_JWT_TOKEN

**Response**:

.. code-block:: json

   {
     "data": [
       {
         "id": 1,
         "name": "Sample Item 1",
         "description": "This is a sample item",
         "created_by": "string",
         "created_at": "timestamp"
       }
     ],
     "total": 1,
     "user": "string"
   }

**Example**:

.. code-block:: bash

   curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     "http://localhost:8005/sample/data"

**Status Codes**:
- `200 OK` - Data retrieved successfully
- `401 Unauthorized` - Invalid or missing JWT token
- `500 Internal Server Error` - Service error

Create Data Item
^^^^^^^^^^^^^^^

Creates a new data item (requires authentication).

**Endpoint**: `POST /sample/data`

**Headers Required**:

.. code-block:: bash

   Authorization: Bearer YOUR_JWT_TOKEN
   Content-Type: application/json

**Request Body**:

.. code-block:: json

   {
     "name": "string",
     "description": "string"
   }

**Response**:

.. code-block:: json

   {
     "id": 1,
     "name": "string",
     "description": "string",
     "created_by": "string",
     "created_at": "timestamp"
   }

**Example**:

.. code-block:: bash

   curl -X POST "http://localhost:8005/sample/data" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"name": "New Item", "description": "A new sample item"}'

**Status Codes**:
- `201 Created` - Item created successfully
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Invalid or missing JWT token
- `500 Internal Server Error` - Service error

Kong Admin API Endpoints
-----------------------

These endpoints are for Kong administration and are not typically used by end users.

List Services
^^^^^^^^^^^^

Lists all services configured in Kong.

**Endpoint**: `GET /services`

**Example**:

.. code-block:: bash

   curl "http://localhost:8006/services"

List Routes
^^^^^^^^^^

Lists all routes configured in Kong.

**Endpoint**: `GET /routes`

**Example**:

.. code-block:: bash

   curl "http://localhost:8006/routes"

Kong Admin List Consumers
^^^^^^^^^^^^^^^^^^^^^^^^

Lists all consumers in Kong.

**Endpoint**: `GET /consumers`

**Example**:

.. code-block:: bash

   curl "http://localhost:8006/consumers"

List Plugins
^^^^^^^^^^^

Lists all plugins configured in Kong.

**Endpoint**: `GET /plugins`

**Example**:

.. code-block:: bash

   curl "http://localhost:8006/plugins"

Error Responses
--------------

All endpoints may return error responses in the following format:

.. code-block:: json

   {
     "error": "string",
     "message": "string",
     "details": "object (optional)"
   }

Common Error Codes
^^^^^^^^^^^^^^^^^

- `400 Bad Request` - Invalid request data or parameters
- `401 Unauthorized` - Missing or invalid authentication
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `409 Conflict` - Resource already exists
- `422 Unprocessable Entity` - Validation errors
- `500 Internal Server Error` - Server error
- `503 Service Unavailable` - Service temporarily unavailable

Rate Limiting
-------------

Currently, no rate limiting is implemented. In production, consider implementing rate limiting to prevent abuse.

CORS Support
-----------

All endpoints support CORS (Cross-Origin Resource Sharing) for web applications:

- **Allowed Origins**: All origins (`*`)
- **Allowed Methods**: GET, POST, PUT, DELETE, OPTIONS
- **Allowed Headers**: Content-Type, Authorization
- **Credentials**: Supported

Testing Endpoints
----------------

You can test all endpoints using:

1. **curl** (command line)
2. **Postman** (GUI tool)
3. **Insomnia** (GUI tool)
4. **Web browsers** (for GET requests)

Example Test Script
^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   #!/bin/bash
   
   # Base URLs
   AUTH_URL="http://localhost:8000"
   GATEWAY_URL="http://localhost:8005"
   
   # Create a user
   echo "Creating user..."
   RESPONSE=$(curl -s -X POST "$AUTH_URL/create-consumer" \
     -H "Content-Type: application/json" \
     -d '{"username": "testuser"}')
   
   # Extract JWT token
   TOKEN=$(echo $RESPONSE | grep -o '"jwt_token":"[^"]*"' | cut -d'"' -f4)
   
   echo "JWT Token: $TOKEN"
   
   # Test protected endpoint
   echo "Testing protected endpoint..."
   curl -H "Authorization: Bearer $TOKEN" \
     "$GATEWAY_URL/sample/status"

Next Steps
----------

Now that you understand the API endpoints:

1. **Try the Examples**: Use the provided examples to test the API
2. **Read the Concepts**: Understand :doc:`../concepts/jwt-authentication` and :doc:`../concepts/kong-gateway`
3. **Explore Configuration**: Learn about configuration options
4. **Build Your Application**: Integrate these endpoints into your application 