# JWT Token Name Issue Fix

## Problem Description

When generating JWT tokens with custom names, users were experiencing "invalid signature" errors when using these tokens with Kong Gateway. This happened specifically when:

1. User provides a custom token name (e.g., "my-custom-token")
2. If that token name already exists, the system generates a unique name (e.g., "my-custom-token_143052_a1b2c3d4")
3. The JWT token was generated with the wrong `kid` claim (using original name instead of the actual unique name)
4. Kong Gateway couldn't validate the token because the `kid` claim didn't match any credential key

## Root Cause

The issue was in the `kong_service.py` file in the `create_jwt_credentials` method and its duplicate handling logic:

1. When a duplicate token name was detected (HTTP 409), the system correctly generated a unique name
2. However, the calling code still used the original token name for JWT generation
3. The JWT `kid` claim contained the original name, but Kong credential key was the unique name
4. This mismatch caused signature validation to fail

## Fix Applied

### 1. Updated Return Types

Modified `create_jwt_credentials` method to return the actual token name used:

```python
# Before
async def create_jwt_credentials(self, username: str, token_name: str) -> Tuple[Dict, str]:
    return jwt_credentials, secret

# After  
async def create_jwt_credentials(self, username: str, token_name: str) -> Tuple[Dict, str, str]:
    return jwt_credentials, secret, actual_token_name
```

### 2. Fixed Duplicate Name Handling

The `_handle_duplicate_token_name` method now properly returns the unique name:

```python
# Before - returned wrong token name
return jwt_credentials, secret

# After - returns actual unique name used
return jwt_credentials, secret, unique_token_name
```

### 3. Updated Token Service

Modified `token_service.py` to use the actual token name for JWT generation:

```python
# Before - used original name
jwt_token, expiration = self.jwt_service.generate_jwt_token(username, token_name, secret)

# After - uses actual name (might be unique if duplicate)
jwt_credentials, secret, actual_token_name = await self.kong_service.create_jwt_credentials(username, token_name)
jwt_token, expiration = self.jwt_service.generate_jwt_token(username, actual_token_name, secret)
```

### 4. Enhanced Logging

Added comprehensive logging to help debug issues:

```python
logger.info(f"JWT credentials created for consumer: {username} with token_name: {token_name}")
logger.info(f"Token name changed from '{token_name}' to '{actual_token_name}' due to conflict")
logger.info(f"JWT token generated for user: {username}, token_name: {token_name}, expires: {expiration}")
```

## Testing the Fix

### Test Case 1: Custom Token Name (No Conflict)
```bash
curl -X POST 'http://localhost:8010/generate-token-auto' \
  -H 'Authorization: Bearer <casdoor_token>' \
  -H 'Content-Type: application/json' \
  -d '{"token_name": "my-unique-token"}'
```

**Expected Result:**
- Token created with name "my-unique-token"
- JWT `kid` claim = "my-unique-token"
- Kong credential key = "my-unique-token"
- Token works with Kong Gateway ✅

### Test Case 2: Custom Token Name (With Conflict)
```bash
# First request
curl -X POST 'http://localhost:8010/generate-token-auto' \
  -H 'Authorization: Bearer <casdoor_token>' \
  -H 'Content-Type: application/json' \
  -d '{"token_name": "duplicate-name"}'

# Second request (same name)
curl -X POST 'http://localhost:8010/generate-token-auto' \
  -H 'Authorization: Bearer <casdoor_token>' \
  -H 'Content-Type: application/json' \
  -d '{"token_name": "duplicate-name"}'
```

**Expected Result:**
- First token: name "duplicate-name"
- Second token: name "duplicate-name_143052_a1b2c3d4" (auto-generated unique)
- Both JWT `kid` claims match their respective Kong credential keys
- Both tokens work with Kong Gateway ✅

### Test Case 3: Auto-Generated Name
```bash
curl -X POST 'http://localhost:8010/generate-token-auto' \
  -H 'Authorization: Bearer <casdoor_token>' \
  -H 'Content-Type: application/json'
```

**Expected Result:**
- Token created with auto-generated name like "username_token_20250819_143052"
- JWT `kid` claim matches the generated name
- Token works with Kong Gateway ✅

## Logs to Verify Fix

When the fix is working correctly, you should see logs like:

```json
{"message": "Generating auto token for user: testuser, requested_name: my-token, using_name: my-token"}
{"message": "JWT credentials created for consumer: testuser with token_name: my-token"}
{"message": "JWT token generated for user: testuser, token_name: my-token, expires: 2026-08-19T06:32:14.425012"}
{"message": "Token generated successfully for user: testuser, final_name: my-token"}
```

Or if there's a conflict:

```json
{"message": "Token name 'my-token' already exists for consumer 'testuser', handling duplicate..."}
{"message": "JWT token name 'my-token' already exists for consumer 'testuser'. Generating unique name."}
{"message": "Retrying with unique token name: my-token_143052_a1b2c3d4"}
{"message": "JWT credentials created successfully with unique name: my-token_143052_a1b2c3d4"}
{"message": "Token name changed from 'my-token' to 'my-token_143052_a1b2c3d4' due to conflict"}
{"message": "Token generated successfully for user: testuser, final_name: my-token_143052_a1b2c3d4"}
```

## Files Modified

1. `/app/services/kong_service.py` - Fixed return types and duplicate handling
2. `/app/services/token_service.py` - Updated to use actual token names
3. `/app/views/token_views.py` - Enhanced logging
4. `/app/views/consumer_views.py` - Enhanced error reporting

## Kong Configuration Required

Ensure your Kong JWT plugin is configured with:

```json
{
  "name": "jwt",
  "config": {
    "key_claim_name": "kid",
    "secret_is_base64": true,
    "claims_to_verify": ["exp"]
  }
}
```

The critical setting is `"key_claim_name": "kid"` which tells Kong to use the `kid` claim to match credential keys.

## Summary

This fix ensures that:
1. ✅ JWT `kid` claim always matches Kong credential key
2. ✅ Duplicate token names are handled gracefully
3. ✅ Custom token names work correctly
4. ✅ Auto-generated names work correctly  
5. ✅ Comprehensive logging for debugging
6. ✅ All tokens work properly with Kong Gateway

The "invalid signature" error should no longer occur when using custom token names.
