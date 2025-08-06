# 🌳 Green Certification - Docker Setup

## Quick Start

### Single Command Startup

```bash
# Production mode (with Nginx, model preloading)
./start.sh

# Development mode (with hot reload)
./start.sh dev
```

## Manual Docker Compose Commands

### Production Deployment
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

### Development Mode
```bash
# Start with development overrides
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Rebuild and start
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

## Services Overview

| Service | Description | Port | Health Check |
|---------|-------------|------|--------------|
| **api** | FastAPI application | 8000 | http://localhost:8000/health |
| **db** | PostgreSQL with PostGIS | 5432 | `pg_isready` |
| **ollama** | Gemma3n model service | 11434 | http://localhost:11434/api/version |
| **nginx** | Reverse proxy | 80 | - |
| **redis** | Caching layer | 6379 | `redis-cli ping` |
| **model-init** | Downloads Gemma model | - | One-time service |

## Access Points

- **API Documentation**: http://localhost:8000/docs
- **API Endpoints**: http://localhost:8000/api/v1/
- **Web Interface**: http://localhost:80
- **Database**: postgresql://postgres:postgres@localhost:5432/green_certification
- **Ollama API**: http://localhost:11434

## Environment Variables

Key environment variables for customization:

```bash
# Database
DATABASE_URL=postgresql://postgres:postgres@db:5432/green_certification
DB_HOST=db
DB_USER=postgres
DB_PASSWORD=postgres

# API
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true

# Ollama/Gemma
OLLAMA_BASE_URL=http://ollama:11434
GEMMA_MODEL_NAME=gemma3n:latest

# Security
SECRET_KEY=your-secret-key-change-in-production
```

## Volume Persistence

- `postgres_data`: Database files
- `ollama_data`: Downloaded models
- `redis_data`: Cache data
- `./uploads`: Uploaded images (host mount)

## Troubleshooting

### Check Service Health
```bash
# Check all containers
docker-compose ps

# Check specific service logs
docker-compose logs api
docker-compose logs ollama
docker-compose logs db
```

### Reset Everything
```bash
# Stop and remove everything including volumes
docker-compose down -v

# Remove all images
docker-compose down --rmi all

# Complete reset
docker system prune -a --volumes
```

### Database Issues
```bash
# Access database directly
docker-compose exec db psql -U postgres -d green_certification

# Run migrations manually
docker-compose exec api alembic upgrade head
```

### Model Issues
```bash
# Re-download Gemma model
docker-compose run --rm model-init

# Check Ollama status
curl http://localhost:11434/api/version
```

## Development Features

In development mode (`./start.sh dev`):

- ✅ **Hot Reload**: File changes trigger automatic restarts
- ✅ **Debug Mode**: Enhanced error messages and logging
- ✅ **Volume Mounting**: Source code changes reflected immediately
- ✅ **No Model Preloading**: Faster startup for development

## Production Features

In production mode (`./start.sh`):

- ✅ **Nginx Reverse Proxy**: Load balancing and static file serving
- ✅ **Model Preloading**: Gemma3n model downloaded on startup
- ✅ **Health Checks**: All services monitored for availability
- ✅ **Redis Caching**: Performance optimization
- ✅ **Optimized Builds**: Minimal container sizes

## Testing the Setup

```bash
# Test API health
curl http://localhost:8000/health

# Test Ollama service
curl http://localhost:11434/api/version

# Test database connection
docker-compose exec api python -c "
from src.database.session import get_db
from src.config.settings import settings
print(f'Database URL: {settings.DATABASE_URL}')
"

# Run the comprehensive test suite
docker-compose exec api python test_api_with_image.py
```

## Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Nginx     │    │  FastAPI    │    │ PostgreSQL  │
│   (Port 80) │────│ (Port 8000) │────│ (Port 5432) │
└─────────────┘    └─────────────┘    └─────────────┘
                           │
                   ┌─────────────┐    ┌─────────────┐
                   │   Ollama    │    │    Redis    │
                   │(Port 11434) │    │ (Port 6379) │
                   └─────────────┘    └─────────────┘
```

## Next Steps

1. **Customize Environment**: Edit `.env` file for your configuration
2. **SSL Setup**: Add SSL certificates for HTTPS in production  
3. **Monitoring**: Integrate with Prometheus/Grafana for monitoring
4. **Scaling**: Use Docker Swarm or Kubernetes for horizontal scaling
5. **Backup**: Set up automated database backups
