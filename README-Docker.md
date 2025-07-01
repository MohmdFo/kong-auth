# Docker Setup for Kong Auth Service

This document explains how to use Docker to run the Kong Auth Service with Kong Gateway.

## Prerequisites

- Docker
- Docker Compose

## Environment Configuration

Before running the services, create a `.env` file based on the example:

```bash
# Copy the example environment file
cp config.env.example .env

# Edit the .env file with your specific values
nano .env
```

### Environment Variables

The following variables are loaded from the `.env` file:

- `KONG_ADMIN_URL`: Kong Admin API URL (default: http://kong:8001)
- `JWT_EXPIRATION_SECONDS`: JWT token expiration time (default: 31536000)
- `PORT`: Service port (default: 8000)
- `HOST`: Service host (default: 0.0.0.0)
- `RELOAD`: Enable auto-reload for development (default: true)

## Quick Start

### Option 1: Run Everything Together (Recommended for Development)

```bash
# Create .env file first
cp config.env.example .env

# Start Kong Gateway, Database, Dashboard, and Auth Service
docker-compose -f docker-compose.full.yml up -d

# Check services
docker-compose -f docker-compose.full.yml ps
```

### Option 2: Run Kong Separately

```bash
# Create .env file first
cp config.env.example .env

# First, start Kong Gateway and Database
docker-compose -f kong/docker-compose.kong.yml up -d

# Wait for Kong to be ready, then start the Auth Service
docker-compose up -d
```

### Option 3: Production Setup

```bash
# Create .env file first
cp config.env.example .env

# Edit .env for production settings
# Set RELOAD=false and adjust other values as needed

# Start Kong Gateway and Database
docker-compose -f kong/docker-compose.kong.yml up -d

# Start the Auth Service in production mode
docker-compose -f docker-compose.prod.yml up -d
```

## Service Endpoints

After starting the services, you can access:

- **Kong Gateway Proxy**: http://localhost:8000
- **Kong Admin API**: http://localhost:8001
- **Kong Dashboard**: http://localhost:8080
- **Kong Auth Service**: http://localhost:${PORT} (default: 8000 or 8002 in full setup)

## Environment Variables

### Kong Auth Service (loaded from .env)
- `KONG_ADMIN_URL`: Kong Admin API URL
- `JWT_EXPIRATION_SECONDS`: JWT token expiration time
- `PORT`: Service port
- `HOST`: Service host
- `RELOAD`: Enable auto-reload for development

### Kong Gateway
- `KONG_DATABASE`: Database type (postgres)
- `KONG_PG_HOST`: PostgreSQL host
- `KONG_PG_USER`: PostgreSQL user
- `KONG_PG_PASSWORD`: PostgreSQL password
- `KONG_PG_DATABASE`: PostgreSQL database name

## Development vs Production

### Development
- Uses volume mounts for live code reloading
- Includes Kong Dashboard for easy management
- Single replica for easier debugging
- `RELOAD=true` in .env file

### Production
- No volume mounts (uses built image)
- Multiple replicas for high availability
- Resource limits and reservations
- `RELOAD=false` in .env file

## Useful Commands

```bash
# View logs
docker-compose -f docker-compose.full.yml logs -f kong-auth

# Stop all services
docker-compose -f docker-compose.full.yml down

# Rebuild and restart
docker-compose -f docker-compose.full.yml up -d --build

# Clean up volumes (WARNING: This will delete Kong data)
docker-compose -f docker-compose.full.yml down -v

# Check Kong health
curl http://localhost:8001/status

# List Kong consumers
curl http://localhost:8001/consumers

# Check environment variables
docker-compose -f docker-compose.full.yml exec kong-auth env | grep -E "(KONG|JWT|PORT)"
```

## Troubleshooting

### Environment Issues
```bash
# Check if .env file exists
ls -la .env

# Verify environment variables are loaded
docker-compose -f docker-compose.full.yml config
```

### Kong Database Issues
```bash
# Check database logs
docker-compose -f kong/docker-compose.kong.yml logs kong-database

# Reset database
docker-compose -f kong/docker-compose.kong.yml down -v
docker-compose -f kong/docker-compose.kong.yml up -d
```

### Auth Service Issues
```bash
# Check auth service logs
docker-compose logs kong-auth

# Rebuild auth service
docker-compose build kong-auth
docker-compose up -d kong-auth
```

### Network Issues
```bash
# Check network connectivity
docker network ls
docker network inspect kong-auth_kong-network
```

## Security Notes

1. **Production**: Change default passwords in Kong configuration
2. **Production**: Enable authentication for Kong Dashboard
3. **Production**: Use secrets management for sensitive data
4. **Production**: Configure proper SSL/TLS certificates
5. **Production**: Set up proper firewall rules
6. **Production**: Never commit .env files to version control

## File Structure

```
kong-auth/
├── Dockerfile                    # Main application Dockerfile
├── docker-compose.yml           # Development compose (auth service only)
├── docker-compose.prod.yml      # Production compose (auth service only)
├── docker-compose.full.yml      # Complete setup (Kong + auth service)
├── kong/
│   ├── docker-compose.kong.yml  # Kong Gateway setup
│   └── kong-dashboard.yml       # Kong Dashboard configuration
├── config.env.example           # Example environment configuration
├── .env                         # Your environment file (create this)
└── .dockerignore                # Docker build exclusions
``` 