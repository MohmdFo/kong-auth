# Kong Auth Service API Examples

This document provides comprehensive curl examples for all endpoints in the Kong Auth Service, including both the authentication service and the protected sample service endpoints.

## 🔑 JWT Token

For all protected endpoints, use this JWT token:
```
Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJ0ZXN0IiwiZXhwIjoxNzgyNzkxOTU2LCJpYXQiOjE3NTEyNTU5NTZ9.a8xATaeQhYQL_BYuDFE-0zU8LpRP2AqM6Xw0HTaPEG8
```

## 📋 Service Endpoints

### Auth Service (Port 8000)
- **Base URL**: `http://localhost:8000`
- **Purpose**: Create consumers and generate JWT tokens
- **Authentication**: None required

### Sample Service (Port 8000 via Kong)
- **Base URL**: `http://localhost:8000`
- **Purpose**: Protected endpoints that require JWT authentication
- **Authentication**: JWT Bearer token required

---

## 🔐 Auth Service Endpoints

### 1. Health Check

```bash
curl -X GET "http://localhost:8000/"
```

**Expected Response:**
```json
{
  "message": "Kong Auth Service is running"
}
```

### 2. Create Consumer and Generate JWT Token

```bash
curl -X POST "http://localhost:8000/create-consumer" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "custom_id": "test-custom-id"
  }'
```

**Expected Response:**
```json
{
  "consumer_id": "uuid-here",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_at": "2024-12-31T23:59:59",
  "secret": "base64-encoded-secret"
}
```

### 3. List All Consumers

```bash
curl -X GET "http://localhost:8000/consumers"
```

**Expected Response:**
```json
{
  "data": [
    {
      "id": "uuid-here",
      "username": "testuser",
      "custom_id": "test-custom-id",
      "created_at": 1703123456
    }
  ]
}
```

### 4. Get Specific Consumer

```bash
curl -X GET "http://localhost:8000/consumers/{consumer_id}"
```

**Expected Response:**
```json
{
  "id": "uuid-here",
  "username": "testuser",
  "custom_id": "test-custom-id",
  "created_at": 1703123456
}
```

### 5. Delete Consumer

```bash
curl -X DELETE "http://localhost:8000/consumers/{consumer_id}"
```

**Expected Response:**
```json
{
  "message": "Consumer deleted successfully"
}
```

---

## 🔒 Protected Sample Service Endpoints

All endpoints below require JWT authentication using the Bearer token.

### 1. Main Sample Endpoint

#### GET Request
```bash
curl -X GET "http://localhost:8000/sample" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJ0ZXN0IiwiZXhwIjoxNzgyNzkxOTU2LCJpYXQiOjE3NTEyNTU5NTZ9.a8xATaeQhYQL_BYuDFE-0zU8LpRP2AqM6Xw0HTaPEG8"
```

#### POST Request
```bash
curl -X POST "http://localhost:8005/sample" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJ0ZXN0IiwiZXhwIjoxNzgyNzkxOTU2LCJpYXQiOjE3NTEyNTU5NTZ9.a8xATaeQhYQL_BYuDFE-0zU8LpRP2AqM6Xw0HTaPEG8" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello from curl!",
    "data": {
      "user_id": 123,
      "action": "test"
    }
  }'
```

### 2. Sample API Endpoint

#### GET Request
```bash
curl -X GET "http://localhost:8000/sample/api" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJ0ZXN0IiwiZXhwIjoxNzgyNzkxOTU2LCJpYXQiOjE3NTEyNTU5NTZ9.a8xATaeQhYQL_BYuDFE-0zU8LpRP2AqM6Xw0HTaPEG8"
```

#### POST Request
```bash
curl -X POST "http://localhost:8000/sample/api" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJ0ZXN0IiwiZXhwIjoxNzgyNzkxOTU2LCJpYXQiOjE3NTEyNTU5NTZ9.a8xATaeQhYQL_BYuDFE-0zU8LpRP2AqM6Xw0HTaPEG8" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "create",
    "resource": "user",
    "data": {
      "name": "John Doe",
      "email": "john@example.com",
      "age": 30
    }
  }'
```

### 3. Sample Status Endpoint

#### GET Request
```bash
curl -X GET "http://localhost:8000/sample/status" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJ0ZXN0IiwiZXhwIjoxNzgyNzkxOTU2LCJpYXQiOjE3NTEyNTU5NTZ9.a8xATaeQhYQL_BYuDFE-0zU8LpRP2AqM6Xw0HTaPEG8"
```

---

## 📊 Expected Responses

### Successful Protected Endpoint Response (GET)
```json
{
  "message": "Hello from Sample Service!",
  "timestamp": 1703123456.789,
  "path": "/sample/status",
  "method": "GET",
  "query_params": {},
  "headers": {
    "user_agent": "curl/7.68.0",
    "content_type": "None",
    "authorization": "Bearer ***"
  },
  "kong_headers": {
    "x_consumer_id": "consumer-uuid",
    "x_consumer_username": "test",
    "x_authenticated_consumer": "consumer-uuid"
  }
}
```

### Successful Protected Endpoint Response (POST)
```json
{
  "message": "POST request received",
  "timestamp": 1703123456.789,
  "path": "/sample/api",
  "method": "POST",
  "body": {
    "action": "create",
    "resource": "user",
    "data": {
      "name": "John Doe",
      "email": "john@example.com",
      "age": 30
    }
  },
  "headers": {
    "user_agent": "curl/7.68.0",
    "content_type": "application/json",
    "authorization": "Bearer ***"
  },
  "kong_headers": {
    "x_consumer_id": "consumer-uuid",
    "x_consumer_username": "test",
    "x_authenticated_consumer": "consumer-uuid"
  }
}
```

### Unauthorized Response (No Token)
```json
{
  "message": "Unauthorized"
}
```

### Invalid Token Response
```json
{
  "message": "Unauthorized"
}
```

---

## 🧪 Testing Scenarios

### 1. Test Without Authentication (Should Fail)
```bash
# These should return 401 Unauthorized
curl -X GET "http://localhost:8000/sample"
curl -X POST "http://localhost:8000/sample/api"
curl -X GET "http://localhost:8000/sample/status"
```

### 2. Test With Invalid Token (Should Fail)
```bash
# These should return 401 Unauthorized
curl -X GET "http://localhost:8000/sample/status" \
  -H "Authorization: Bearer invalid.token.here"

curl -X GET "http://localhost:8000/sample/status" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
```

### 3. Test With Valid Token (Should Succeed)
```bash
# All these should return 200 OK with data
curl -X GET "http://localhost:8000/sample/status" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJ0ZXN0IiwiZXhwIjoxNzgyNzkxOTU2LCJpYXQiOjE3NTEyNTU5NTZ9.a8xATaeQhYQL_BYuDFE-0zU8LpRP2AqM6Xw0HTaPEG8"
```

---

## 🔧 Environment Variables

Make sure these environment variables are set:

```bash
export KONG_ADMIN_URL="http://localhost:8006"
export JWT_EXPIRATION_SECONDS="31536000"
```

---

## 📝 Notes

1. **JWT Token Expiration**: The provided token expires on `2024-12-31T23:59:59`
2. **Consumer Username**: The token is issued for consumer `test`
3. **Kong Headers**: Kong will pass consumer information in headers like `X-Consumer-ID` and `X-Consumer-Username`
4. **CORS Support**: All endpoints support CORS for cross-origin requests
5. **Error Handling**: All endpoints return appropriate HTTP status codes and error messages

---

## 🚀 Quick Test Script

```bash
#!/bin/bash

TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJ0ZXN0IiwiZXhwIjoxNzgyNzkxOTU2LCJpYXQiOjE3NTEyNTU5NTZ9.a8xATaeQhYQL_BYuDFE-0zU8LpRP2AqM6Xw0HTaPEG8"

echo "Testing Auth Service..."
curl -s "http://localhost:8000/" | jq '.'

echo -e "\nTesting Protected Endpoints..."
echo "GET /sample/status:"
curl -s -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/sample/status" | jq '.'

echo -e "\nPOST /sample/api:"
curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}' \
  "http://localhost:8000/sample/api" | jq '.'
``` 