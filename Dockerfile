FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads/images

# Set environment variables
ENV PYTHONPATH=/app \
    API_HOST=0.0.0.0 \
    API_PORT=8000 \
    DEBUG=false

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "main.py"]