#!/bin/bash

# Green Certification - Docker Compose Startup Script

set -e

echo "🌳 Green Certification - Docker Startup"
echo "======================================="

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Parse command line arguments
MODE="production"
if [[ "$1" == "dev" || "$1" == "development" ]]; then
    MODE="development"
fi

echo "🚀 Starting in $MODE mode..."

if [[ "$MODE" == "development" ]]; then
    echo "📝 Development features:"
    echo "  - File watching and hot reload"
    echo "  - Debug mode enabled"
    echo "  - Source code mounted as volume"
    echo ""
    
    docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build
else
    echo "🏭 Production features:"
    echo "  - Nginx reverse proxy"
    echo "  - Model pre-loading"
    echo "  - Optimized builds"
    echo ""
    
    # Build and start services
    docker-compose up --build -d
    
    echo ""
    echo "✅ Services starting up..."
    echo "📊 Checking service health..."
    
    # Wait for services to be healthy
    sleep 20
    
    echo ""
    echo "🌐 Service URLs:"
    echo "  - API:           http://localhost:8000"
    echo "  - Documentation: http://localhost:8000/docs"
    echo "  - Web Interface: http://localhost:80"
    echo "  - Database:      localhost:5432"
    echo "  - Ollama:        http://localhost:11434"
    echo ""
    
    # Show running containers
    echo "📋 Running containers:"
    docker-compose ps
    
    echo ""
    echo "📝 Useful commands:"
    echo "  - View logs:     docker-compose logs -f"
    echo "  - Stop services: docker-compose down"
    echo "  - Restart API:   docker-compose restart api"
fi

echo ""
echo "🎉 Green Certification is ready!"
