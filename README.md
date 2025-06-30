# Kong Auth Service

A FastAPI application that creates Kong consumers and generates JWT tokens for authentication.

## Features

- Create Kong consumers with JWT credentials
- Generate JWT tokens with configurable expiration
- List and manage Kong consumers
- Automatic handling of existing consumers

## Prerequisites

- Python 3.8+
- Kong Gateway running with Admin API accessible
- JWT plugin configured in Kong

## Installation

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