# Green Duty - Project Start Guide

## Quick Start

This guide will help you get the Green Duty API up and running on your local machine.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Docker & Docker Compose** (Recommended - easiest setup)
- **Python 3.9+** (for local development)
- **PostgreSQL 14+** (if running without Docker)
- **Git** (to clone the repository)

## Option 1: Docker Setup (Recommended)

### 1. Clone and Setup Environment

```bash
# Clone the repository
git clone <your-repo-url>
cd green-duty

# Copy environment file
cp .env.example .env
```

### 2. Configure Environment Variables

Edit the `.env` file and update the following values:

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true

# Database Configuration (Docker will handle this)
DATABASE_URL=postgresql://postgres:postgres@db:5432/green_duty

# Gemma API Configuration
GEMMA_API_KEY=your_gemma_api_key_here
OLLAMA_API_URL=http://localhost:11434/api

# Storage Configuration
STORAGE_BUCKET=green-duty
STORAGE_TYPE=local

# Logging
LOG_LEVEL=INFO
UVICORN_LOG_LEVEL=INFO
```

### 3. Start the Application

```bash
# Build and start all services
docker-compose up -d

# View logs (optional)
docker-compose logs -f api
```

### 4. Verify Installation

- API will be available at: `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`
- Database: `localhost:5432` (postgres/postgres)

## Option 2: Local Development Setup

### 1. Clone and Setup Environment

```bash
# Clone the repository
git clone <your-repo-url>
cd green-duty

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Setup PostgreSQL Database

```bash
# Install PostgreSQL (macOS with Homebrew)
brew install postgresql
brew services start postgresql

# Create database
createdb green_duty

# Or using psql
psql -c "CREATE DATABASE green_duty;"
```

### 3. Configure Environment

```bash
# Copy environment file
cp .env.example .env
```

Edit `.env` file:
```bash
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/green_duty
GEMMA_API_KEY=your_gemma_api_key_here
# ... other configurations
```

### 4. Run Database Migrations

```bash
# Initialize Alembic (if not already done)
alembic init alembic

# Run migrations
alembic upgrade head
```

### 5. Start the Application

```bash
# Run the application
python main.py
```

## Setting up Ollama and Gemma Model

The Green Duty system uses Ollama to run the Gemma model locally for tree analysis.

### 1. Install Ollama

```bash
# macOS
brew install ollama

# Or download from https://ollama.ai
```

### 2. Start Ollama Service

```bash
# Start Ollama service
ollama serve
```

### 3. Pull Gemma Model

```bash
# Pull the Gemma model (this may take a while)
ollama pull gemma3n

# Or use a smaller model for testing
ollama pull gemma3n
```

### 4. Update Configuration

Update your `.env` file:
```bash
OLLAMA_API_URL=http://localhost:11434/api
GEMMA_MODEL_NAME=gemma3n
```

## Project Structure

```
green-duty/
├── src/                     # Source code
│   ├── api/                 # FastAPI application and routes
│   │   ├── routes/          # API endpoint definitions
│   │   └── app.py           # Main FastAPI app
│   ├── config/              # Configuration settings
│   ├── database/            # Database models and session
│   ├── models/              # Pydantic schemas
│   ├── services/            # Business logic services
│   └── utils/               # Utility functions
├── docs/                    # Documentation
├── migrations/              # Database migrations
├── uploads/                 # File upload directory
├── docker-compose.yml       # Docker services configuration
├── Dockerfile              # Docker image definition
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
└── .env.example            # Environment variables template
```

## API Endpoints

Once running, you can access these endpoints:

### Upload API
- `POST /api/v1/upload` - Upload tree images with location data
- `GET /api/v1/upload/{upload_id}` - Get upload details
- `GET /api/v1/uploads/user/{user_id}` - List user uploads

### Analysis API
- `POST /api/v1/analyze/{upload_id}` - Analyze uploaded tree images
- `GET /api/v1/analysis/{analysis_id}` - Get analysis results
- `GET /api/v1/analyses/upload/{upload_id}` - Get analysis for upload

### Certification API
- `POST /api/v1/certify/{analysis_id}` - Generate certification
- `GET /api/v1/certification/{certification_id}` - Get certification details
- `GET /api/v1/certifications/analysis/{analysis_id}` - Get certification for analysis

## Testing the API

### 1. Using the Interactive Documentation

Visit `http://localhost:8000/docs` to access the Swagger UI where you can:
- View all available endpoints
- Test API calls directly from the browser
- See request/response schemas

### 2. Using curl

```bash
# Health check
curl http://localhost:8000/health

# Upload tree images (example)
curl -X POST "http://localhost:8000/api/v1/upload" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "latitude": 40.7128,
    "longitude": -74.0060,
    "images": ["base64_encoded_image_data"],
    "additional_notes": "Oak tree in Central Park"
  }'
```

## Common Issues and Solutions

### Issue: Database Connection Error
```bash
# Check if PostgreSQL is running
brew services list | grep postgresql

# Restart PostgreSQL
brew services restart postgresql
```

### Issue: Ollama Model Not Found
```bash
# List available models
ollama list

# Pull the required model
ollama pull gemma:7b
```

### Issue: Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process (replace PID)
kill -9 <PID>

# Or use a different port in .env
API_PORT=8001
```

### Issue: Docker Permission Denied
```bash
# Add user to docker group (Linux)
sudo usermod -aG docker $USER

# Restart Docker Desktop (macOS/Windows)
```

## Development Workflow

### 1. Making Changes

```bash
# Make your changes to the 