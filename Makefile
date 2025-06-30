.PHONY: help build up down restart logs clean test dev prod setup

# Default target
help:
	@echo "Kong Auth Service - Docker Compose Management"
	@echo ""
	@echo "Available commands:"
	@echo "  build     - Build all Docker images"
	@echo "  up        - Start all services (production)"
	@echo "  down      - Stop all services"
	@echo "  restart   - Restart all services"
	@echo "  logs      - Show logs from all services"
	@echo "  clean     - Remove all containers, networks, and volumes"
	@echo "  test      - Run tests"
	@echo "  dev       - Start development environment"
	@echo "  prod      - Start production environment"
	@echo "  setup     - Run Kong setup only"
	@echo "  status    - Show status of all services"

# Build all images
build:
	@echo "🔨 Building Docker images..."
	docker-compose build

# Start production environment
up:
	@echo "🚀 Starting production environment..."
	docker-compose up -d
	@echo "✅ Services started!"
	@echo "📋 Available endpoints:"
	@echo "  - Auth Service: http://localhost:8000"
	@echo "  - Sample Service: http://localhost:8001"
	@echo "  - Kong Gateway: http://localhost:8005"
	@echo "  - Kong Admin: http://localhost:8006"

# Start development environment
dev:
	@echo "🚀 Starting development environment..."
	docker-compose -f docker-compose.dev.yml up -d
	@echo "✅ Development services started!"
	@echo "📋 Available endpoints:"
	@echo "  - Auth Service: http://localhost:8000 (with hot reload)"
	@echo "  - Sample Service: http://localhost:8001"
	@echo "  - Kong Gateway: http://localhost:8005"
	@echo "  - Kong Admin: http://localhost:8006"
	@echo "  - Adminer: http://localhost:8080 (if tools profile enabled)"

# Start production environment with nginx
prod:
	@echo "🚀 Starting production environment with nginx..."
	docker-compose --profile production up -d
	@echo "✅ Production services started!"
	@echo "📋 Available endpoints:"
	@echo "  - Nginx: http://localhost:80"
	@echo "  - Kong Gateway: http://localhost:8005"
	@echo "  - Kong Admin: http://localhost:8006"

# Stop all services
down:
	@echo "🛑 Stopping all services..."
	docker-compose down
	docker-compose -f docker-compose.dev.yml down

# Restart all services
restart:
	@echo "🔄 Restarting all services..."
	docker-compose restart
	docker-compose -f docker-compose.dev.yml restart

# Show logs
logs:
	@echo "📋 Showing logs from all services..."
	docker-compose logs -f

# Show development logs
logs-dev:
	@echo "📋 Showing development logs..."
	docker-compose -f docker-compose.dev.yml logs -f

# Clean everything
clean:
	@echo "🧹 Cleaning up all containers, networks, and volumes..."
	docker-compose down -v --remove-orphans
	docker-compose -f docker-compose.dev.yml down -v --remove-orphans
	docker system prune -f
	@echo "✅ Cleanup completed!"

# Run tests
test:
	@echo "🧪 Running tests..."
	docker-compose exec auth-service python -m pytest tests/ -v

# Run Kong setup only
setup:
	@echo "🔧 Running Kong setup..."
	docker-compose run --rm kong-setup

# Show status
status:
	@echo "📊 Service Status:"
	@echo "=================="
	@docker-compose ps
	@echo ""
	@echo "🔍 Health Checks:"
	@echo "=================="
	@docker-compose exec kong curl -s http://localhost:8006/status | jq '.'
	@docker-compose exec auth-service curl -s http://localhost:8000/ | jq '.'
	@docker-compose exec sample-service curl -s http://localhost:8001/ | jq '.'

# Create consumer and get token
create-consumer:
	@echo "🔐 Creating consumer and getting JWT token..."
	@curl -s -X POST "http://localhost:8000/create-consumer" \
		-H "Content-Type: application/json" \
		-d '{"username": "testuser", "custom_id": "test-custom-id"}' | jq '.'

# Test protected endpoint
test-protected:
	@echo "🧪 Testing protected endpoint..."
	@echo "First, create a consumer:"
	@echo "make create-consumer"
	@echo ""
	@echo "Then use the token to test:"
	@echo "curl -H 'Authorization: Bearer YOUR_TOKEN' http://localhost:8005/sample/status"

# Show all endpoints
endpoints:
	@echo "🌐 Available Endpoints:"
	@echo "======================"
	@echo "Auth Service (No Auth Required):"
	@echo "  GET  http://localhost:8000/"
	@echo "  POST http://localhost:8000/create-consumer"
	@echo "  GET  http://localhost:8000/consumers"
	@echo "  GET  http://localhost:8000/consumers/{id}"
	@echo "  DELETE http://localhost:8000/consumers/{id}"
	@echo ""
	@echo "Protected Endpoints (JWT Required):"
	@echo "  GET/POST http://localhost:8005/sample"
	@echo "  GET/POST http://localhost:8005/sample/api"
	@echo "  GET      http://localhost:8005/sample/status"
	@echo ""
	@echo "Management:"
	@echo "  Kong Admin: http://localhost:8006"
	@echo "  Sample Service (Direct): http://localhost:8001"

# Quick start for development
quick-dev:
	@echo "⚡ Quick development setup..."
	@make dev
	@sleep 10
	@make setup
	@echo "✅ Development environment ready!"
	@make endpoints 