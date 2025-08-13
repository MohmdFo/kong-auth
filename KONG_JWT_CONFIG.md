# Kong JWT Configuration Guide

This document explains the Kong JWT plugin configuration and recent changes made to fix JWT authentication issues.

## Overview

Our Kong Auth Service generates JWT tokens for consumers and uses Kong's JWT plugin for authentication. This guide covers the proper configuration and recent fixes to ensure tokens work correctly.

## Kong JWT Plugin Configuration

### Required Configuration

To use the new JWT token format with `kid` (Key ID) claims, your Kong JWT plugin must be configured as follows:

```python
plugin_data = {
    "name": "jwt",
    "config": {
        "uri_param_names": ["jwt"],
        "cookie_names": ["jwt"],
        "key_claim_name": "kid",  # ⚠️ CHANGED: Use 'kid' instead of 'iss'
        "secret_is_base64": True,
        "claims_to_verify": ["exp"],
        "anonymous": None,
        "run_on_preflight": True,
        "maximum_expiration": 31536000,
        "header_names": ["authorization"]
    }
}
```

### Key Configuration Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| `key_claim_name` | `"kid"` | **CRITICAL**: Must be `"kid"` to match our new token format |
| `secret_is_base64` | `true` | Our secrets are base64-encoded |
| `claims_to_verify` | `["exp"]` | Verify token expiration |
| `header_names` | `["authorization"]` | Accept tokens in Authorization header |
| `uri_param_names` | `["jwt"]` | Accept tokens as URL parameter |
| `cookie_names` | `["jwt"]` | Accept tokens in cookies |

## Recent Changes - JWT Token Format Update

### Problem We Fixed

**Before (Broken)**:
- Kong credential `key` = `token_name` (e.g., "user_token_20250813_143000")
- JWT `iss` claim = `username` (e.g., "john_doe")
- Kong config: `key_claim_name: "iss"`
- **Result**: Kong couldn't find credential because `token_name ≠ username`
- **Error**: `"No credentials found for given 'iss'"`

**After (Fixed)**:
- Kong credential `key` = `token_name` (e.g., "user_token_20250813_143000")
- JWT `iss` claim = `username` (e.g., "john_doe")
- JWT `kid` claim = `token_name` (e.g., "user_token_20250813_143000")
- Kong config: `key_claim_name: "kid"`
- **Result**: Kong finds credential by matching `kid` claim with credential `key`

### New JWT Token Structure

Our JWT tokens now include both `iss` and `kid` claims:

```json
{
  "iss": "john_doe",                           // User identifier
  "kid": "john_doe_token_20250813_143000",     // Kong credential key
  "exp": 1723660800,                           // Expiration timestamp
  "iat": 1723574400                            // Issued at timestamp
}
```

### Code Changes Made

1. **JWT Payload Generation**:
   ```python
   # Before
   payload = {
       "iss": username,
       "exp": int(expiration.timestamp()),
       "iat": int(datetime.utcnow().timestamp()),
   }
   
   # After
   payload = {
       "iss": username,              # User identifier
       "kid": token_name,            # Kong credential key
       "exp": int(expiration.timestamp()),
       "iat": int(datetime.utcnow().timestamp()),
   }
   ```

2. **Kong Credential Creation** (unchanged):
   ```python
   jwt_payload = {
       "key": token_name,           # This matches the 'kid' claim
       "secret": secret_base64,
       "algorithm": "HS256"
   }
   ```

## How to Apply Changes

### 1. Update Kong Plugin Configuration

You need to update your Kong JWT plugin configuration to use `key_claim_name: "kid"`:

**Via Kong Admin API**:
```bash
curl -X PATCH http://your-kong-admin:8001/plugins/{plugin-id} \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "key_claim_name": "kid"
    }
  }'
```

**Via Kong Configuration File**:
```yaml
plugins:
- name: jwt
  config:
    key_claim_name: kid
    secret_is_base64: true
    claims_to_verify:
    - exp
    header_names:
    - authorization
    uri_param_names:
    - jwt
    cookie_names:
    - jwt
```

### 2. Restart Kong

After updating the configuration:
```bash
kong reload
# or
kong restart
```

### 3. Generate New Tokens

Use your updated service endpoints to generate new tokens:

```bash
# Generate a new token
curl -X POST 'https://your-service/generate-token-auto' \
  -H 'Authorization: Bearer <casdoor_token>' \
  -H 'Content-Type: application/json' \
  -d '{"token_name": "my_token"}'
```

### 4. Test Authentication

Test the new token with your Kong-protected service:

```bash
curl -X POST 'https://gw.ai-lab.ir/llm/v1/chat/completions' \
  -H 'Authorization: Bearer <new_jwt_token>' \
  -H 'Content-Type: application/json' \
  -d '{"model":"sharif-qwen/qwen3-14b","messages":[{"role":"user","content":"test"}]}'
```

## Benefits of the New Approach

1. **Multiple Tokens Per User**: Users can have multiple JWT tokens with unique names
2. **Clear Separation**: `iss` identifies the user, `kid` identifies the specific token
3. **JWT Best Practices**: Uses standard `kid` claim for key identification
4. **Backward Compatibility**: Existing consumers continue to work

## Troubleshooting

### Common Issues

1. **"No credentials found for given 'kid'"**
   - Ensure Kong plugin uses `key_claim_name: "kid"`
   - Verify the token was generated after the code changes

2. **"Invalid signature"**
   - Check that `secret_is_base64: true` in Kong config
   - Verify the secret matches between Kong credential and JWT signing

3. **Token expired**
   - Check `JWT_EXPIRATION_SECONDS` environment variable
   - Generate a new token

### Debugging Steps

1. **Check Kong Plugin Config**:
   ```bash
   curl http://your-kong-admin:8001/plugins/{plugin-id}
   ```

2. **Decode JWT Token** (for debugging):
   ```bash
   # Use jwt.io or
   echo "your.jwt.token" | cut -d. -f2 | base64 -d | jq
   ```

3. **Check Kong Credentials**:
   ```bash
   curl http://your-kong-admin:8001/consumers/{username}/jwt
   ```

## Environment Variables

Ensure these environment variables are set:

```bash
KONG_ADMIN_URL=http://localhost:8001
JWT_EXPIRATION_SECONDS=31536000  # 1 year
```

## API Endpoints

The service provides these endpoints for JWT management:

- `POST /generate-token-auto` - Generate JWT token for authenticated user
- `POST /auto-generate-consumer` - Create consumer and token in one call
- `GET /my-tokens` - List user's JWT tokens
- `DELETE /my-tokens/{jwt_id}` - Delete specific token
- `DELETE /my-tokens/by-name/{token_name}` - Delete token by name

## Security Considerations

1. **Secret Management**: Secrets are randomly generated and base64-encoded
2. **Token Expiration**: All tokens have configurable expiration times
3. **User Isolation**: Each user's tokens are isolated by consumer
4. **Audit Trail**: All operations are logged and metrified

## Migration Notes

If you're migrating from the old format:

1. Update Kong plugin configuration first
2. Generate new tokens using the updated service
3. Old tokens will stop working once Kong config is updated
4. No consumer or credential deletion is required

---

For more information, see the main [README.md](./README.md) or contact the development team.
