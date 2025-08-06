# 🌳 Green Certification - Quick Setup Guide

## 🚀 **Single Command Startup**

```bash
# Start everything (production mode)
./start.sh

# Start in development mode (with hot reload)
./start.sh dev
```

## 📋 **What You Get**

✅ **Complete API Backend**
- FastAPI server with tree identification
- Interactive API docs at http://localhost:8000/docs

✅ **Database Ready**
- PostgreSQL with PostGIS extensions
- Automatic schema migrations

✅ **AI Model Integration**
- Ollama service with Gemma3n model
- Automatic model downloading

✅ **Production Features**
- Nginx reverse proxy
- Redis caching
- Health checks for all services

## 🔧 **Quick Commands**

```bash
# View logs
docker-compose logs -f api

# Stop everything
docker-compose down

# Restart just the API
docker-compose restart api

# Access database
docker-compose exec db psql -U postgres -d green_certification

# Test the API
curl http://localhost:8000/health
```

## 📊 **Service Endpoints**

| Service | URL | Purpose |
|---------|-----|---------|
| API Docs | http://localhost:8000/docs | Interactive API documentation |
| API Health | http://localhost:8000/health | Service health check |
| Upload API | http://localhost:8000/api/v1/uploads | Upload tree images |
| Analysis API | http://localhost:8000/api/v1/analysis | Get tree species identification |
| Certification | http://localhost:8000/api/v1/certifications | Get green certification scores |

## 🧪 **Testing**

```bash
# Run the comprehensive test suite
docker-compose exec api python test_api_with_image.py
```

This will test the complete workflow:
1. Image processing with OpenCV
2. Gemma3n model for species identification
3. Certification scoring algorithm
4. Full API integration

---

**Need help?** Check `DOCKER_README.md` for detailed documentation!
