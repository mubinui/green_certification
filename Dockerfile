FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install UV package manager
RUN pip install uv

WORKDIR /app

# Copy dependency files
COPY pyproject.toml requirements.txt ./

# Install Python dependencies using UV
RUN uv venv && \
    uv pip install -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads/images test_images

# Set environment variables
ENV PYTHONPATH=/app \
    API_HOST=0.0.0.0 \
    API_PORT=8000 \
    DEBUG=false \
    PATH="/app/.venv/bin:$PATH"

# Add health check endpoint
COPY <<EOF /app/health_check.py
from fastapi import FastAPI
from fastapi.responses import JSONResponse

def add_health_check(app: FastAPI):
    @app.get("/health")
    async def health_check():
        return JSONResponse({"status": "healthy", "service": "green-certification-api"})
EOF

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "main.py"]