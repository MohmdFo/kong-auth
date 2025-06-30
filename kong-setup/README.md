# Kong Setup and Testing

This directory contains everything you need to set up Kong with a sample service and test your JWT authentication flow.

## 📁 Files

- `sample-service.py` - A simple HTTP server that acts as your backend service
- `setup-kong.py` - Script to automatically configure Kong services and routes
- `test-complete-flow.py` - Comprehensive test script for the entire flow
- `README.md` - This file

## 🚀 Quick Start

### 1. Start Your Auth Service

First, make sure your FastAPI auth service is running:

```bash
# In the main project directory
python run.py
```

### 2. Start the Sample Service

In a new terminal, start the sample service:

```bash
# In the kong-setup directory
python sample-service.py
```

This will start a simple HTTP server on port 8001 that Kong will proxy to.

### 3. Set Up Kong

Configure Kong with the sample service:

```bash
# In the kong-setup directory
python setup-kong.py
```

This will:
- Create a service called "sample-service" pointing to `http://localhost:8001`
- Create routes for `/sample`, `/sample/api`, and `/sample/status`
- Enable JWT plugin with your configuration
- Enable CORS plugin for cross-origin requests

### 4. Test the Complete Flow

Run the comprehensive test:

```bash
# In the kong-setup directory
python test-complete-flow.py
```

This will test:
- Auth service functionality
- Sample service accessibility
- Protected endpoints without tokens (should fail)
- Protected endpoints with valid tokens (should succeed)
- Invalid token handling

## 🔧 Configuration

### Environment Variables

You can customize the setup by setting these environment variables:

```bash
export KONG_ADMIN_URL="http://localhost:8006"
export SAMPLE_SERVICE_URL="http://localhost:8001"
```

### Kong Setup Options

The setup script supports several options:

```bash
# Basic setup
python setup-kong.py

# Custom Kong admin URL
python setup-kong.py --admin-url http://localhost:8006

# Custom sample service URL
python setup-kong.py --service-url http://localhost:8001

# Clean up Kong configuration
python setup-kong.py --cleanup
```

## 📋 Available Endpoints

After setup, these endpoints will be available through Kong:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `http://localhost:8000/sample` | GET, POST | Main endpoint |
| `http://localhost:8000/sample/api` | GET, POST | API endpoint |
| `http://localhost:8000/sample/status` | GET | Status endpoint |

**All endpoints require JWT authentication!**

## 🧪 Testing

### Manual Testing

1. **Create a consumer and get a JWT token:**
   ```bash
   curl -X POST "http://localhost:8000/create-consumer" \
     -H "Content-Type: application/json" \
     -d '{"username": "testuser"}'
   ```

2. **Test protected endpoint with token:**
   ```bash
   curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     http://localhost:8000/sample/status
   ```

3. **Test without token (should fail):**
   ```bash
   curl http://localhost:8000/sample/status
   ```

### Automated Testing

Run the complete test suite:

```bash
python test-complete-flow.py
```

## 🔍 Sample Service Features

The sample service provides:

- **GET requests**: Returns information about the request including Kong headers
- **POST requests**: Echoes back the request body
- **CORS support**: Handles preflight requests
- **Kong header inspection**: Shows consumer information passed by Kong

### Sample Response

```json
{
  "message": "Hello from Sample Service!",
  "timestamp": 1703123456.789,
  "path": "/sample/status",
  "method": "GET",
  "headers": {
    "user_agent": "curl/7.68.0",
    "content_type": "None",
    "authorization": "Bearer ***"
  },
  "kong_headers": {
    "x_consumer_id": "consumer-uuid",
    "x_consumer_username": "testuser",
    "x_authenticated_consumer": "consumer-uuid"
  }
}
```

## 🛠️ Troubleshooting

### Common Issues

1. **Kong Admin API not accessible:**
   - Make sure Kong is running: `kong start`
   - Check Kong admin URL: `curl http://localhost:8006/status`

2. **Sample service not accessible:**
   - Make sure the service is running: `python sample-service.py`
   - Check the service URL: `curl http://localhost:8001/`

3. **JWT authentication failing:**
   - Verify JWT plugin configuration in Kong
   - Check that the token is properly formatted
   - Ensure the consumer exists in Kong

4. **CORS issues:**
   - The setup includes CORS plugin configuration
   - Check browser console for CORS errors

### Clean Up

To remove the Kong configuration:

```bash
python setup-kong.py --cleanup
```

This will delete the service, routes, and plugins created by the setup script.

## 📊 Monitoring

You can monitor Kong's activity through:

- **Kong Admin API**: `http://localhost:8006`
- **Kong Gateway**: `http://localhost:8000`
- **Sample Service Logs**: Check the terminal running `sample-service.py`

## 🔐 Security Notes

- The sample service is for testing only
- JWT tokens have a 1-year expiration
- All endpoints are protected by JWT authentication
- CORS is configured for development (allows all origins)
- Kong headers reveal consumer information to the backend service 