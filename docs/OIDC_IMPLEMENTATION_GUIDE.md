# Casdoor OIDC Implementation Guide

This guide provides a comprehensive implementation of OpenID Connect (OIDC) authentication with Casdoor in your FastAPI backend, including proper JWT validation, user authorization, and resource ownership enforcement.

## Overview

The implementation uses the official Casdoor Python SDK and follows OIDC standards to provide:
- Secure JWT token validation using JWKS (JSON Web Key Set)
- Automatic key rotation support
- User resource ownership enforcement
- Role-based and permission-based access control
- Production-ready error handling and logging

## Architecture

```
Frontend → Casdoor (OIDC Provider) → FastAPI Backend → Kong Gateway
    ↓              ↓                      ↓              ↓
Login Flow    JWT Token           Validate Token    Route Traffic
    ↓              ↓                      ↓              ↓
Get Token    Issue JWT           Extract User      Apply Policies
    ↓              ↓                      ↓              ↓
API Calls    Bearer Token        Check Ownership   Manage Consumers
```

## Key Components

### 1. CasdoorOIDC Class
- Handles JWT token validation using JWKS
- Manages user information retrieval
- Provides OIDC flow utilities

### 2. CasdoorUser Class
- Represents authenticated users with OIDC claims
- Implements resource ownership logic
- Provides role and permission checking

### 3. FastAPI Dependencies
- `get_current_user`: Required authentication
- `get_optional_user`: Optional authentication
- `require_roles`: Role-based access control
- `require_permissions`: Permission-based access control
- `require_resource_ownership`: Resource ownership enforcement

## Configuration

### Environment Variables

```bash
# Casdoor Configuration
CASDOOR_ENDPOINT=https://iam.ai-lab.ir
CASDOOR_CLIENT_ID=f83fb202807419aee818
CASDOOR_CLIENT_SECRET=33189aeb03ec21c7fe65ab0d9b00f4ba198bc640
CASDOOR_ORG_NAME=built-in
CASDOOR_APP_NAME=app-built-in
CASDOOR_CERT_PATH=casdoor_cert.pem
```

### Certificate File
Place your Casdoor certificate file (`casdoor_cert.pem`) in the project root directory.

## Implementation Details

### JWT Token Validation

The system validates JWT tokens using multiple layers:

1. **JWKS Key Resolution**: Automatically fetches public keys from Casdoor's JWKS endpoint
2. **Token Verification**: Validates signature, expiration, audience, and issuer
3. **User Information**: Retrieves user details from Casdoor API
4. **Claims Extraction**: Extracts OIDC claims for authorization

```python
# Token validation flow
token → JWKS lookup → Signature verification → Claims extraction → User info → Authorization
```

### Resource Ownership Enforcement

Users can only access resources they own:

```python
def can_access_resource(self, resource_owner: str) -> bool:
    # User can access their own resources
    if resource_owner == self.name or resource_owner == self.id:
        return True
    
    # Admin users can access all resources
    if "admin" in self.roles:
        return True
        
    # Check specific permissions
    if "manage_all_consumers" in self.permissions:
        return True
        
    return False
```

### Authorization Decorators

#### Role-Based Access Control
```python
@app.get("/admin-only")
async def admin_endpoint(user: CasdoorUser = Depends(require_roles(["admin"]))):
    return {"message": "Admin access granted"}
```

#### Permission-Based Access Control
```python
@app.get("/manage-consumers")
async def manage_consumers(user: CasdoorUser = Depends(require_permissions(["manage_consumers"]))):
    return {"message": "Consumer management access granted"}
```

#### Resource Ownership
```python
@app.get("/consumers/{consumer_id}")
async def get_consumer(
    consumer_id: str,
    user: CasdoorUser = Depends(require_resource_ownership("consumer_id"))
):
    # User can only access their own consumers
    return {"consumer": consumer_id}
```

## API Usage Examples

### Frontend Integration

#### 1. OIDC Login Flow
```javascript
// Redirect to Casdoor for authentication
const authUrl = `${CASDOOR_ENDPOINT}/login/oauth/authorize?` +
    `client_id=${CLIENT_ID}&` +
    `response_type=code&` +
    `redirect_uri=${REDIRECT_URI}&` +
    `scope=openid profile email&` +
    `state=${state}`;

window.location.href = authUrl;
```

#### 2. Token Exchange
```javascript
// Exchange authorization code for tokens
const response = await fetch(`${CASDOOR_ENDPOINT}/api/login/oauth/access_token`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        grant_type: 'authorization_code',
        client_id: CLIENT_ID,
        client_secret: CLIENT_SECRET,
        code: authCode,
        redirect_uri: REDIRECT_URI
    })
});

const tokens = await response.json();
const accessToken = tokens.access_token;
```

#### 3. API Calls
```javascript
// Make authenticated API calls
const response = await fetch('/api/me', {
    headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
    }
});

const userInfo = await response.json();
```

### Backend API Examples

#### Get Current User
```python
@app.get("/me")
async def get_current_user_info(current_user: CasdoorUser = Depends(get_current_user)):
    return current_user.to_dict()
```

#### Create Consumer (Ownership Enforced)
```python
@app.post("/create-consumer")
async def create_consumer(
    consumer_data: ConsumerRequest,
    current_user: CasdoorUser = Depends(get_current_user)
):
    # Users can only create consumers with their own username
    if consumer_data.username != current_user.name and "admin" not in current_user.roles:
        raise HTTPException(status_code=403, detail="You can only create consumers with your own username")
    
    # Create consumer logic...
```

#### Access Own Resources
```python
@app.get("/consumers/{consumer_id}")
async def get_consumer(
    consumer_id: str,
    current_user: CasdoorUser = Depends(require_resource_ownership("consumer_id"))
):
    # User can only access their own consumers
    return {"consumer": consumer_id}
```

## Security Best Practices

### 1. Token Validation
- Always validate JWT signatures
- Check token expiration
- Verify audience and issuer claims
- Use HTTPS in production

### 2. Key Rotation
- JWKS automatically handles key rotation
- Keys are cached with expiration
- Fallback to certificate file if JWKS unavailable

### 3. Error Handling
- Don't expose sensitive information in error messages
- Log authentication failures for monitoring
- Implement rate limiting for authentication endpoints

### 4. Resource Protection
- Always check resource ownership
- Use principle of least privilege
- Implement audit logging for sensitive operations

## Production Considerations

### 1. Performance
- Cache JWKS keys with appropriate TTL
- Use connection pooling for HTTP clients
- Implement token caching if needed

### 2. Monitoring
- Log authentication events
- Monitor token validation failures
- Track resource access patterns

### 3. Error Handling
```python
try:
    user = await casdoor_oidc.verify_token(token)
except jwt.ExpiredSignatureError:
    # Handle expired tokens
    raise HTTPException(status_code=401, detail="Token expired")
except jwt.InvalidTokenError:
    # Handle invalid tokens
    raise HTTPException(status_code=401, detail="Invalid token")
except Exception as e:
    # Handle other errors
    logger.error(f"Token verification failed: {e}")
    raise HTTPException(status_code=500, detail="Authentication service error")
```

### 4. Health Checks
```python
@app.get("/health/auth")
async def auth_health_check():
    try:
        # Test JWKS endpoint
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{CASDOOR_ENDPOINT}/.well-known/jwks.json")
            if response.status_code == 200:
                return {"status": "healthy", "jwks": "available"}
            else:
                return {"status": "unhealthy", "jwks": "unavailable"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

## Testing

### Unit Tests
```python
def test_user_can_access_own_resource():
    user = CasdoorUser(user_data, token_claims)
    assert user.can_access_resource(user.name) == True

def test_user_cannot_access_other_resource():
    user = CasdoorUser(user_data, token_claims)
    assert user.can_access_resource("other_user") == False

def test_admin_can_access_all_resources():
    user_data["roles"] = ["admin"]
    user = CasdoorUser(user_data, token_claims)
    assert user.can_access_resource("any_user") == True
```

### Integration Tests
```python
async def test_authenticated_endpoint():
    headers = {"Authorization": f"Bearer {valid_token}"}
    response = await client.get("/me", headers=headers)
    assert response.status_code == 200

async def test_unauthorized_access():
    headers = {"Authorization": f"Bearer {invalid_token}"}
    response = await client.get("/me", headers=headers)
    assert response.status_code == 401
```

## Troubleshooting

### Common Issues

1. **JWKS Connection Errors**
   - Check Casdoor endpoint availability
   - Verify network connectivity
   - Check certificate validity

2. **Token Validation Failures**
   - Verify token format
   - Check audience and issuer claims
   - Ensure token hasn't expired

3. **Resource Access Denied**
   - Verify user permissions
   - Check resource ownership
   - Review role assignments

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Migration from Previous Implementation

If migrating from the previous authentication system:

1. **Update imports**:
   ```python
   # Old
   from .casdoor_auth import get_current_user
   
   # New
   from .casdoor_oidc import get_current_user
   ```

2. **Update environment variables**:
   ```bash
   # Add new variables
   CASDOOR_CLIENT_ID=your_client_id
   CASDOOR_CLIENT_SECRET=your_client_secret
   ```

3. **Test thoroughly**:
   - Verify all endpoints work with new authentication
   - Test resource ownership enforcement
   - Validate error handling

## Conclusion

This OIDC implementation provides a secure, scalable, and standards-compliant authentication system for your FastAPI backend. It enforces proper resource ownership, supports role-based access control, and handles key rotation automatically.

The system is production-ready and follows security best practices while maintaining ease of use and flexibility for different authorization scenarios. 