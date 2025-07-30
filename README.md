# Kong Auth Service

A FastAPI application that creates Kong consumers, generates JWT tokens for authentication, and provides a comprehensive API for managing Kong services and routes.

## Features

- Create Kong consumers with JWT credentials
- Generate JWT tokens with configurable expiration
- List and manage Kong consumers
- **NEW**: Complete Kong service and route management API
- **NEW**: Dynamic service creation and configuration
- **NEW**: Plugin management (JWT, CORS, Rate Limiting, etc.)
- **NEW**: Service health monitoring
- **NEW**: Complete service setup with routes and plugins
- Automatic handling of existing consumers
- Complete Docker support with development and production configurations
- Comprehensive testing and CI/CD pipeline

## Quick Start

Get up and running in 5 minutes:

```bash
# Clone the repository
git clone <repository-url>
cd kong-auth

# Start all services with Docker
make quick-dev

# Create your first user and get JWT token
curl -X POST "http://localhost:8000/create-consumer" \
  -H "Content-Type: application/json" \
  -d '{"username": "myuser"}'

# Create a Kong service and route
curl -X POST "http://localhost:8000/kong/services" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-api",
    "url": "http://localhost:3000",
    "protocol": "http",
    "tags": ["production"]
  }'

# Test authentication
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  http://localhost:8005/sample/status
```

## Documentation

📚 **Comprehensive Documentation Available!**

We've created detailed documentation that explains everything in simple terms, even for non-developers:

### 📖 [Read the Full Documentation](docs/)

The documentation covers:

- **🔐 [JWT Authentication Guide](docs/CASDOOR_AUTH_README.md)**: How tokens work, why we use them, and how they're generated
- **🔑 [OIDC Implementation Guide](docs/OIDC_IMPLEMENTATION_GUIDE.md)**: Complete OpenID Connect implementation with Casdoor
- **🏢 [Kong Gateway Deep Dive](docs/kong-management-api.md)**: Understanding the two essential plugins (JWT and CORS) and their configurations
- **🏗️ System Architecture**: Complete overview of how everything works together
- **🚀 Quick Start Guide**: Get up and running in 5 minutes
- **📋 [API Reference](docs/api-examples.md)**: Complete endpoint documentation with examples
- **🔧 Configuration Guide**: How to customize the system
- **🐳 [Docker Setup](docs/README-Docker.md)**: Development and production deployment
- **🧪 Testing Guide**: How to test your setup
- **❓ FAQ**: Common questions and answers

### 🎯 Perfect for Everyone

- **👨‍💻 Developers**: API reference, integration examples, code snippets
- **👨‍💼 Business Users**: Security explanations, architecture overview, benefits
- **👨‍🔧 DevOps Engineers**: Deployment guides, monitoring, production setup
- **👨‍🎓 Beginners**: Step-by-step tutorials, real-world analogies, troubleshooting

### 🏗️ Building the Documentation

```bash
# Install documentation dependencies
cd docs
pip install -r requirements.txt

# Build HTML documentation
make html

# Serve locally
make serve
```

The documentation will be available at `http://localhost:8080`.

## Testing

Run the test suite to verify your setup:

```bash
# Run all tests
python -m pytest tests/

# Run specific test
python tests/test_casdoor_auth.py

# Verify Casdoor setup
python tests/verify_casdoor_setup.py
```

## Examples

Check out the examples in `docs/examples/`:

- **OIDC Authentication**: `docs/examples/example_oidc_usage.py`
- **Kong API Usage**: `docs/examples/example_kong_api_usage.py`
- **Basic Usage**: `docs/examples/example_usage.py`

## Project Structure

```
kong-auth/
├── app/                    # Main application code
│   ├── main.py            # FastAPI application entry point
│   ├── kong_api.py        # Kong management API endpoints
│   ├── kong_manager.py    # Kong management logic
│   ├── casdoor_oidc.py    # OIDC authentication with Casdoor
│   └── logging_config.py  # Logging configuration
├── docs/                   # Documentation
│   ├── examples/          # Code examples and usage
│   ├── source/            # Sphinx documentation source
│   └── *.md              # Markdown documentation files
├── tests/                  # Test files
│   ├── test_*.py         # Unit and integration tests
│   └── verify_*.py       # Setup verification scripts
├── kong/                   # Kong configuration files
├── kong-setup/            # Kong setup scripts
├── logs/                   # Application logs
├── config.env.example     # Environment configuration template
├── requirements.txt       # Python dependencies
├── run.py                 # Application runner
└── docker-compose*.yml    # Docker configurations
```

## Prerequisites

- Python 3.8+
- Kong Gateway running with Admin API accessible
- JWT plugin configured in Kong
- Docker and Docker Compose (for containerized deployment)

## Installation

### Option 1: Docker (Recommended)

```bash
# Development setup
make quick-dev

# Production setup
make prod
```

### Option 2: Local Installation

1. Clone the repository and navigate to the project directory:
```bash
cd kong-auth
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables (copy from config.env.example):
```bash
cp config.env.example .env
```

Edit the `.env` file with your Kong configuration:
```env
KONG_ADMIN_URL=http://localhost:8006
JWT_EXPIRATION_SECONDS=31536000
```

## Running the Application

### Docker (Recommended)

```bash
# Development with hot reload
make dev

# Production
make prod

# Stop all services
make down
```

### Local Development

Start the FastAPI server:
```bash
python -m app.main
```

Or using uvicorn directly:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Kong Management API (NEW!)

The Kong Management API provides a complete REST interface for managing Kong services, routes, and plugins:

#### Service Management
- `POST /kong/services` - Create a new service
- `GET /kong/services` - List all services
- `GET /kong/services/{service_name}` - Get specific service
- `PATCH /kong/services/{service_name}` - Update service
- `DELETE /kong/services/{service_name}` - Delete service

#### Route Management
- `POST /kong/routes` - Create a new route
- `GET /kong/routes` - List all routes
- `GET /kong/routes/{route_name}` - Get specific route
- `PATCH /kong/routes/{route_name}` - Update route
- `DELETE /kong/routes/{route_name}` - Delete route

#### Plugin Management
- `POST /kong/services/{service_name}/plugins` - Enable plugin on service
- `GET /kong/plugins` - List all plugins
- `DELETE /kong/plugins/{plugin_id}` - Delete plugin

#### Health and Monitoring
- `GET /kong/services/{service_name}/health` - Get service health
- `GET /kong/status` - Get Kong API status

#### Complete Service Setup
- `POST /kong/services/complete` - Setup complete service with routes and plugins

📖 **See [Kong Management API Documentation](docs/kong-management-api.md) for complete details and examples.**

### Consumer Management API
```http
POST /create-consumer
Content-Type: application/json

{
  "username": "myuser",
  "custom_id": "optional-custom-id"
}
```

Response:
```json
{
  "consumer_id": "uuid",
  "token": "jwt-token",
  "expires_at": "2024-12-31T23:59:59",
  "secret": "base64-encoded-secret"
}
```

### List All Consumers
```http
GET /consumers
```

### Get Specific Consumer
```http
GET /consumers/{consumer_id}
```

### Delete Consumer
```http
DELETE /consumers/{consumer_id}
```

## Kong JWT Plugin Configuration

Make sure your Kong JWT plugin is configured with these settings:

- **Key claim name**: `iss`
- **Secret is base64**: `true`
- **Claims to verify**: `exp`
- **Maximum expiration**: `31536000`
- **Header names**: `authorization`

## Usage Examples

### Kong Management API

#### Create a Service with Routes and Plugins
```bash
# Create a complete service setup
curl -X POST "http://localhost:8000/kong/services/complete" \
  -H "Content-Type: application/json" \
  -d '{
    "service": {
      "name": "my-api",
      "url": "http://localhost:3000",
      "protocol": "http",
      "tags": ["production"]
    },
    "routes": [
      {
        "name": "my-api-main",
        "service_name": "my-api",
        "paths": ["/api/v1"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "strip_path": true
      }
    ],
    "plugins": [
      {
        "name": "jwt",
        "config": {
          "uri_param_names": ["jwt"],
          "key_claim_name": "iss",
          "secret_is_base64": true,
          "claims_to_verify": ["exp"],
          "header_names": ["authorization"]
        },
        "enabled": true
      },
      {
        "name": "cors",
        "config": {
          "origins": ["*"],
          "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
          "headers": ["Content-Type", "Authorization"],
          "credentials": true
        },
        "enabled": true
      }
    ]
  }'
```

#### Check Service Health
```bash
curl "http://localhost:8000/kong/services/my-api/health"
```

#### List All Services
```bash
curl "http://localhost:8000/kong/services"
```

### Consumer Management API

1. Create a consumer and get a JWT token:
```bash
curl -X POST "http://localhost:8000/create-consumer" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser"}'
```

2. Use the token in requests to your Kong-protected services:
```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  http://your-kong-gateway/your-service
```

## API Documentation

Once the server is running, you can access:
- Interactive API docs: `http://localhost:8000/docs`
- ReDoc documentation: `http://localhost:8000/redoc`

## Testing

### Kong Management API Tests

Test the new Kong Management API functionality:

```bash
# Start Kong for testing (if not already running)
./start-kong-for-testing.sh

# Run comprehensive API tests
python test_kong_api.py

# Run example usage
python example_kong_api_usage.py
```

**Note**: The Kong Management API requires Kong Gateway to be running. If tests fail with connection errors, ensure Kong is started first.

### Consumer Management API Tests

```bash
# Run all tests
make test

# Run specific test file
python -m pytest test_api.py

# Test complete flow
python kong-setup/test-complete-flow.py
```

## Docker Commands

```bash
# Development
make dev          # Start development environment
make quick-dev    # Quick development setup
make down         # Stop all services

# Production
make prod         # Start production environment
make build        # Build all images
make logs         # View logs

# Maintenance
make clean        # Clean up containers and volumes
make rebuild      # Rebuild all images
```

## Error Handling

The application handles common scenarios:
- Consumer already exists (returns existing consumer)
- Kong Admin API errors
- Invalid requests
- Missing consumers
- Kong connection issues (503 Service Unavailable)
- Kong timeout issues (504 Gateway Timeout)

## Troubleshooting

### Kong Management API Issues

**Connection Errors (503 Service Unavailable)**
- Ensure Kong Gateway is running: `docker-compose -f kong/docker-compose.kong.yml up -d`
- Check Kong Admin API: `curl http://localhost:8006/status`
- Verify Kong Admin URL in environment: `KONG_ADMIN_URL=http://localhost:8006`

**Timeout Errors (504 Gateway Timeout)**
- Kong may be overloaded or slow to respond
- Check Kong logs: `docker-compose -f kong/docker-compose.kong.yml logs`
- Restart Kong if necessary

**JSON Serialization Errors**
- Fixed in latest version - ensure you're using the updated code
- Check that URL fields are strings, not HttpUrl objects

### Quick Fixes

```bash
# Start Kong for testing
./start-kong-for-testing.sh

# Check Kong status
curl http://localhost:8006/status

# View Kong logs
docker-compose -f kong/docker-compose.kong.yml logs

# Restart Kong
docker-compose -f kong/docker-compose.kong.yml restart
```

## Security Notes

- JWT secrets are generated randomly for each consumer
- Tokens expire after the configured time period
- The application uses HS256 algorithm for JWT signing
- Secrets are base64 encoded as required by Kong

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

- 📚 **Documentation**: [docs/](docs/) - Comprehensive guides and explanations
- ❓ **FAQ**: [docs/source/faq.rst](docs/source/faq.rst) - Common questions and answers
- 🐛 **Issues**: Report bugs and request features
- 💬 **Discussions**: Join community discussions

---

**🎉 Ready to get started?** Check out our [Quick Start Guide](docs/source/guides/quick-start.rst) or dive into the [Complete Documentation](docs/)! 