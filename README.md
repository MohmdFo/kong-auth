# Kong Auth Service

A FastAPI application that creates Kong consumers and generates JWT tokens for authentication.

## Features

- Create Kong consumers with JWT credentials
- Generate JWT tokens with configurable expiration
- List and manage Kong consumers
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

# Test authentication
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  http://localhost:8005/sample/status
```

## Documentation

📚 **Comprehensive Documentation Available!**

We've created detailed documentation that explains everything in simple terms, even for non-developers:

### 📖 [Read the Full Documentation](docs/)

The documentation covers:

- **🔐 JWT Authentication Explained**: How tokens work, why we use them, and how they're generated
- **🏢 Kong Gateway Deep Dive**: Understanding the two essential plugins (JWT and CORS) and their configurations
- **🏗️ System Architecture**: Complete overview of how everything works together
- **🚀 Quick Start Guide**: Get up and running in 5 minutes
- **📋 API Reference**: Complete endpoint documentation with examples
- **🔧 Configuration Guide**: How to customize the system
- **🐳 Docker Setup**: Development and production deployment
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

### Create Consumer and Generate Token
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

## Usage Example

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