# Casdoor Authentication Integration

This document explains how to set up and use Casdoor authentication with your Kong Auth Service API.

## Overview

The API now requires authentication using Casdoor JWT tokens. All protected endpoints require a valid Casdoor token in the `Authorization` header.

## Configuration

### Environment Variables

Add the following environment variables to your `.env` file:

```bash
# Casdoor Configuration
CASDOOR_ENDPOINT=https://your-endponit
CASDOOR_CLIENT_ID=your-id
CASDOOR_CLIENT_SECRET=your-id
CASDOOR_ORG_NAME=ogname
CASDOOR_APP_NAME=app-name
```

### Configuration Options

- `CASDOOR_ENDPOINT`: The URL of your Casdoor instance
- `CASDOOR_CLIENT_ID`: Your Casdoor application client ID
- `CASDOOR_CLIENT_SECRET`: Your Casdoor application client secret
- `CASDOOR_ORG_NAME`: The organization name in Casdoor (default: "built-in")
- `CASDOOR_APP_NAME`: The application name in Casdoor (default: "app-built-in")
- `casdoor_cert.pem`: Certificate file containing the public key for JWT verification

### Certificate File

The `casdoor_cert.pem` file should be placed in the root directory of your project. This file contains the public key used to verify JWT tokens from Casdoor.

## Authentication Flow

1. **Frontend obtains token**: Your frontend application authenticates with Casdoor and receives a JWT token
2. **API calls**: Frontend includes the token in the `Authorization` header
3. **Token verification**: The API verifies the token with Casdoor
4. **Access granted**: If valid, the user can access protected endpoints

## API Usage

### Making Authenticated Requests

Include the Casdoor token in the `Authorization` header:

```bash
curl -H "Authorization: Bearer YOUR_CASDOOR_TOKEN" \
     http://localhost:8000/me
```

### Example with JavaScript/Fetch

```javascript
const token = 'your_casdoor_token_here';

fetch('http://localhost:8000/me', {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
})
.then(response => response.json())
.then(data => console.log(data));
```

### Example with Python/Requests

```python
import requests

token = 'your_casdoor_token_here'
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

response = requests.get('http://localhost:8000/me', headers=headers)
user_info = response.json()
print(f"Authenticated user: {user_info['name']}")
```

## Protected Endpoints

All the following endpoints now require authentication:

### Consumer Management
- `POST /create-consumer` - Create a new Kong consumer
- `POST /generate-token` - Generate a new JWT token
- `GET /consumers` - List all consumers
- `GET /consumers/{consumer_id}` - Get specific consumer
- `DELETE /consumers/{consumer_id}` - Delete consumer
- `GET /consumers/{username}/tokens` - List user tokens
- `DELETE /consumers/{username}/tokens/{jwt_id}` - Delete token

### Kong Management
- `GET /kong/services` - List Kong services
- `POST /kong/services` - Create Kong service
- `GET /kong/services/{service_name}` - Get specific service
- `PATCH /kong/services/{service_name}` - Update service
- `DELETE /kong/services/{service_name}` - Delete service
- `GET /kong/routes` - List Kong routes
- `POST /kong/routes` - Create Kong route
- `GET /kong/routes/{route_name}` - Get specific route
- `PATCH /kong/routes/{route_name}` - Update route
- `DELETE /kong/routes/{route_name}` - Delete route
- `GET /kong/plugins` - List Kong plugins
- `POST /kong/services/{service_name}/plugins` - Enable plugin
- `DELETE /kong/plugins/{plugin_id}` - Delete plugin
- `GET /kong/services/{service_name}/health` - Get service health
- `POST /kong/services/complete` - Setup complete service
- `GET /kong/status` - Get Kong status

### User Information
- `GET /me` - Get current user information

## Public Endpoints

The following endpoints do not require authentication:

- `GET /` - Root endpoint (health check)

## Error Responses

### 401 Unauthorized
```json
{
  "detail": "Invalid or expired token"
}
```

### 403 Forbidden
```json
{
  "detail": "Access denied. Required roles: [admin]"
}
```

## Testing

Use the provided test script to verify authentication:

```bash
# Test without authentication
python test_casdoor_auth.py

# Test with authentication
python test_casdoor_auth.py YOUR_CASDOOR_TOKEN
```

## Getting a Casdoor Token

1. **Login to Casdoor**: Access your Casdoor instance
2. **Navigate to Profile**: Go to your user profile
3. **Copy Access Token**: Find and copy your access token
4. **Use in API**: Include the token in your API requests

## Advanced Features

### Role-Based Access Control

You can implement role-based access control using the `require_roles` decorator:

```python
from app.casdoor_auth import require_roles

@app.get("/admin-only")
async def admin_endpoint(user: CasdoorUser = Depends(require_roles(["admin"]))):
    return {"message": "Admin access granted"}
```

### Permission-Based Access Control

You can implement permission-based access control using the `require_permissions` decorator:

```python
from app.casdoor_auth import require_permissions

@app.get("/manage-consumers")
async def manage_consumers(user: CasdoorUser = Depends(require_permissions(["manage_consumers"]))):
    return {"message": "Consumer management access granted"}
```

## Troubleshooting

### Common Issues

1. **Token Expired**: Casdoor tokens have an expiration time. Get a new token if you receive 401 errors.

2. **Invalid Token Format**: Ensure the token is included as `Bearer <token>` in the Authorization header.

3. **Casdoor Connection Issues**: Check that your Casdoor instance is running and accessible at the configured endpoint.

4. **Configuration Errors**: Verify all environment variables are set correctly.
5. **Certificate File Missing**: Ensure `casdoor_cert.pem` is present in the project root directory.

### Debug Mode

Enable debug logging to see detailed authentication information:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Security Considerations

1. **Token Storage**: Store tokens securely on the client side
2. **Token Expiration**: Handle token expiration gracefully
3. **HTTPS**: Use HTTPS in production for secure token transmission
4. **Token Refresh**: Implement token refresh logic for long-running applications 