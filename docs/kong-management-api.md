# Kong Management API Documentation

## Overview

The Kong Management API provides a RESTful interface for managing Kong services, routes, and plugins through your main application. This API allows users to define their own services and paths without directly accessing Kong's Admin API.

## Base URL

```
http://localhost:8000/kong
```

## Authentication

Currently, the API doesn't require authentication. In production, you should implement proper authentication and authorization.

## API Endpoints

### Service Management

#### Create Service
**POST** `/kong/services`

Creates a new Kong service.

**Request Body:**
```json
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
```

**Response:**
```json
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
```

#### List Services
**GET** `/kong/services`

Returns all Kong services.

**Response:**
```json
[
  {
    "id": "uuid",
    "name": "my-service",
    "url": "http://localhost:8001",
    "protocol": "http",
    "created_at": 1234567890
  }
]
```

#### Get Service
**GET** `/kong/services/{service_name}`

Returns a specific Kong service.

**Response:**
```json
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
```

#### Update Service
**PATCH** `/kong/services/{service_name}`

Updates an existing Kong service.

**Request Body:**
```json
{
  "url": "http://localhost:8002",
  "connect_timeout": 30000,
  "tags": ["staging", "api"]
}
```

**Response:**
```json
{
  "id": "uuid",
  "name": "my-service",
  "url": "http://localhost:8002",
  "protocol": "http",
  "connect_timeout": 30000,
  "tags": ["staging", "api"],
  "updated_at": 1234567890
}
```

#### Delete Service
**DELETE** `/kong/services/{service_name}`

Deletes a Kong service.

**Response:**
```json
{
  "message": "Service 'my-service' deleted successfully"
}
```

### Route Management

#### Create Route
**POST** `/kong/routes`

Creates a new Kong route.

**Request Body:**
```json
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
```

**Response:**
```json
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
```

#### List Routes
**GET** `/kong/routes`

Returns all Kong routes.

**Query Parameters:**
- `service_name` (optional): Filter routes by service name

**Response:**
```json
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
```

#### Get Route
**GET** `/kong/routes/{route_name}`

Returns a specific Kong route.

**Response:**
```json
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
```

#### Update Route
**PATCH** `/kong/routes/{route_name}`

Updates an existing Kong route.

**Request Body:**
```json
{
  "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
  "strip_path": false,
  "tags": ["api", "v1", "updated"]
}
```

**Response:**
```json
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
```

#### Delete Route
**DELETE** `/kong/routes/{route_name}`

Deletes a Kong route.

**Response:**
```json
{
  "message": "Route 'my-route' deleted successfully"
}
```

### Plugin Management

#### Enable Plugin
**POST** `/kong/services/{service_name}/plugins`

Enables a plugin on a service.

**Request Body:**
```json
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
```

**Response:**
```json
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
```

#### List Plugins
**GET** `/kong/plugins`

Returns all Kong plugins.

**Query Parameters:**
- `service_name` (optional): Filter plugins by service name

**Response:**
```json
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
]
```

#### Delete Plugin
**DELETE** `/kong/plugins/{plugin_id}`

Deletes a Kong plugin.

**Response:**
```json
{
  "message": "Plugin 'uuid' deleted successfully"
}
```

### Health and Status

#### Get Service Health
**GET** `/kong/services/{service_name}/health`

Returns health information for a service.

**Response:**
```json
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
```

#### Get Kong Status
**GET** `/kong/status`

Returns Kong API status.

**Response:**
```json
{
  "status": "healthy",
  "kong_admin_url": "http://localhost:8006",
  "services_count": 5
}
```

### Complete Service Setup

#### Setup Complete Service
**POST** `/kong/services/complete`

Sets up a complete service with routes and plugins in one request.

**Request Body:**
```json
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
```

**Response:**
```json
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
```

## Error Responses

All endpoints return standard HTTP status codes:

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource already exists
- `500 Internal Server Error`: Server error

Error response format:
```json
{
  "detail": "Error message describing what went wrong"
}
```

## Usage Examples

### Using curl

#### Create a service:
```bash
curl -X POST http://localhost:8000/kong/services \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-api",
    "url": "http://localhost:3000",
    "protocol": "http",
    "tags": ["production"]
  }'
```

#### Create a route:
```bash
curl -X POST http://localhost:8000/kong/routes \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-api-route",
    "service_name": "my-api",
    "paths": ["/api/v1"],
    "methods": ["GET", "POST", "PUT", "DELETE"],
    "strip_path": true
  }'
```

#### Enable JWT plugin:
```bash
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
```

### Using Python

See `example_kong_api_usage.py` for comprehensive Python examples.

## Best Practices

1. **Service Naming**: Use descriptive, unique names for services
2. **Route Paths**: Use versioned paths (e.g., `/api/v1`, `/api/v2`)
3. **Tags**: Use tags to organize and categorize services, routes, and plugins
4. **Error Handling**: Always handle potential errors in your client code
5. **Health Checks**: Regularly check service health using the health endpoint
6. **Cleanup**: Remove unused services and routes to keep Kong clean

## Configuration

The API uses the following environment variables:

- `KONG_ADMIN_URL`: Kong Admin API URL (default: `http://localhost:8006`)
- `API_BASE_URL`: Your API base URL (default: `http://localhost:8000`)

## Security Considerations

1. **Authentication**: Implement proper authentication for production use
2. **Authorization**: Add role-based access control
3. **Rate Limiting**: Consider implementing rate limiting on the API
4. **Input Validation**: All inputs are validated using Pydantic models
5. **HTTPS**: Use HTTPS in production environments
6. **CORS**: Configure CORS appropriately for your use case

## Troubleshooting

### Common Issues

1. **Service already exists**: Use PATCH to update instead of POST to create
2. **Route not found**: Ensure the service exists before creating routes
3. **Plugin configuration errors**: Check Kong plugin documentation for valid config options
4. **Connection errors**: Verify Kong Admin API is accessible

### Debugging

1. Check Kong status: `GET /kong/status`
2. Check service health: `GET /kong/services/{service_name}/health`
3. Review application logs for detailed error messages
4. Verify Kong Admin API connectivity

## Migration from setup-kong.py

If you're migrating from the static `setup-kong.py` script:

1. Replace static service definitions with API calls
2. Use the complete service setup endpoint for complex configurations
3. Implement dynamic service management based on your application needs
4. Add proper error handling and retry logic 