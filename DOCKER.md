# Docker Setup for Kong Auth Service

This document explains how to run the Kong Auth Service using Docker Compose.

## 🚀 Quick Start

### Prerequisites
- Docker
- Docker Compose
- Make (optional, for easier management)

### Quick Development Setup
```bash
# Start everything with one command
make quick-dev
```

### Manual Setup
```bash
# 1. Build images
docker-compose build

# 2. Start services
docker-compose up -d

# 3. Run Kong setup
docker-compose run --rm kong-setup
```

## 📁 Docker Files

### Main Files
- `docker-compose.yml` - Production configuration
- `docker-compose.dev.yml` - Development configuration with hot reload
- `Dockerfile.auth` - Auth service production image
- `Dockerfile.auth.dev` - Auth service development image
- `Dockerfile.sample` - Sample service production image
- `Dockerfile.sample.dev` - Sample service development image
- `Dockerfile.setup` - Kong setup service image
- `Makefile` - Management commands

## 🏗️ Services Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Auth Service  │    │  Sample Service │    │   Kong Gateway  │
│   (Port 8000)   │    │   (Port 8001)   │    │   (Port 8005)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Kong Admin    │
                    │   (Port 8006)   │
                    └─────────────────┘
```

## 🔧 Service Configuration

### Kong Gateway
- **Image**: `kong:3.4`
- **Gateway Port**: 8005
- **Admin Port**: 8006
- **Database**: Off (stateless)
- **Logging**: JSON format to stdout/stderr

### Auth Service (FastAPI)
- **Image**: Custom Python 3.11
- **Port**: 8000
- **Features**: JWT token generation, consumer management
- **Environment**: Hot reload in development

### Sample Service
- **Image**: Custom Python 3.11
- **Port**: 8001
- **Features**: Protected endpoints, Kong header inspection
- **Purpose**: Testing and demonstration

### Kong Setup Service
- **Image**: Custom Python 3.11
- **Purpose**: One-time Kong configuration
- **Actions**: Creates services, routes, and plugins

## 🎯 Usage Commands

### Using Makefile (Recommended)
```bash
# Show all available commands
make help

# Development environment
make dev

# Production environment
make up

# Stop all services
make down

# Show logs
make logs

# Clean everything
make clean

# Show service status
make status

# Create consumer and get token
make create-consumer

# Show all endpoints
make endpoints
```

### Using Docker Compose Directly
```bash
# Development
docker-compose -f docker-compose.dev.yml up -d

# Production
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild images
docker-compose build --no-cache
```

## 🌐 Available Endpoints

### After Setup
| Service | URL | Description |
|---------|-----|-------------|
| Auth Service | http://localhost:8000 | JWT token generation |
| Sample Service | http://localhost:8001 | Direct access (bypass Kong) |
| Kong Gateway | http://localhost:8005 | Protected endpoints |
| Kong Admin | http://localhost:8006 | Kong management API |

### Protected Endpoints (via Kong)
- `GET/POST http://localhost:8005/sample`
- `GET/POST http://localhost:8005/sample/api`
- `GET http://localhost:8005/sample/status`

## 🔐 Authentication Flow

1. **Create Consumer**:
   ```bash
   curl -X POST "http://localhost:8000/create-consumer" \
     -H "Content-Type: application/json" \
     -d '{"username": "testuser"}'
   ```

2. **Use JWT Token**:
   ```bash
   curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     http://localhost:8005/sample/status
   ```

## 🧪 Testing

### Quick Test
```bash
# 1. Create consumer
make create-consumer

# 2. Test protected endpoint
make test-protected
```

### Manual Testing
```bash
# Test auth service
curl http://localhost:8000/

# Test sample service directly
curl http://localhost:8001/

# Test Kong admin
curl http://localhost:8006/status
```

## 🔍 Monitoring and Logs

### View Logs
```bash
# All services
make logs

# Development logs
make logs-dev

# Specific service
docker-compose logs -f auth-service
```

### Health Checks
```bash
# Check service status
make status

# Manual health checks
curl http://localhost:8000/  # Auth service
curl http://localhost:8001/  # Sample service
curl http://localhost:8006/status  # Kong
```

## 🛠️ Development

### Hot Reload
The development environment includes hot reload for the auth service:
- Code changes are automatically detected
- Service restarts automatically
- No need to rebuild containers

### Development vs Production
| Feature | Development | Production |
|---------|-------------|------------|
| Hot Reload | ✅ | ❌ |
| Volume Mounts | ✅ | ❌ |
| Debug Logging | ✅ | ❌ |
| Optimized Images | ❌ | ✅ |
| Health Checks | ✅ | ✅ |

## 🚀 Production Deployment

### Basic Production
```bash
make prod
```

### Custom Production Setup
```bash
# Build optimized images
docker-compose build --no-cache

# Start with nginx
docker-compose --profile production up -d

# Check status
docker-compose ps
```

### Environment Variables
Create a `.env` file for production:
```env
KONG_ADMIN_URL=http://kong:8006
JWT_EXPIRATION_SECONDS=31536000
HOST=0.0.0.0
PORT=8000
```

## 🧹 Cleanup

### Remove Everything
```bash
make clean
```

### Manual Cleanup
```bash
# Stop and remove containers
docker-compose down -v

# Remove images
docker-compose down --rmi all

# Remove volumes
docker volume prune

# Remove networks
docker network prune
```

## 🔧 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Check what's using the port
   lsof -i :8005
   
   # Stop conflicting services
   docker-compose down
   ```

2. **Kong Not Starting**
   ```bash
   # Check Kong logs
   docker-compose logs kong
   
   # Restart Kong
   docker-compose restart kong
   ```

3. **Services Not Ready**
   ```bash
   # Check health status
   make status
   
   # Wait for services
   sleep 30
   ```

4. **Permission Issues**
   ```bash
   # Fix file permissions
   sudo chown -R $USER:$USER .
   
   # Rebuild images
   docker-compose build --no-cache
   ```

### Debug Mode
```bash
# Run with debug output
docker-compose up

# Check specific service
docker-compose logs auth-service
```

## 📊 Performance

### Resource Usage
- **Kong**: ~50MB RAM
- **Auth Service**: ~100MB RAM
- **Sample Service**: ~50MB RAM
- **Total**: ~200MB RAM

### Scaling
```bash
# Scale auth service
docker-compose up -d --scale auth-service=3

# Scale sample service
docker-compose up -d --scale sample-service=2
```

## 🔒 Security

### Best Practices
- Services run as non-root users
- Health checks enabled
- Network isolation with custom bridge
- No sensitive data in images
- JWT tokens with expiration

### Network Security
- Internal communication via `kong-network`
- External access only through exposed ports
- Kong acts as reverse proxy and security layer

## 📝 Notes

- Kong setup runs once and exits
- Development environment includes Redis for caching
- Production environment includes nginx for load balancing
- All services have health checks
- Logs are in JSON format for easy parsing
- Makefile provides convenient shortcuts 