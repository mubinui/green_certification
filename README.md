# Green Certification API

A tree analysis and certification system that uses image processing and AI to identify tree species, analyze their environmental impact, and provide certification recommendations.

## Features

- Upload tree images with geographic location data
- Analyze tree images to identify species and estimate age
- Evaluate tree certification based on environmental impact
- Generate recommendations for tree maintenance and care

## Tech Stack

- FastAPI - Web framework for building APIs
- SQLAlchemy - SQL toolkit and ORM
- PostgreSQL - Database backend
- Gemma 3n - AI model for tree species identification
- Docker & Docker Compose - Containerization and orchestration

## Project Structure

```
green_certification/
├── docs/                    # Documentation files
│   ├── prd.md               # Product Requirements Document
│   ├── system_design.md     # System Design Document
│   ├── class_diagram.mermaid # Class diagram
│   └── sequence_diagram.mermaid # Sequence diagram
├── src/                     # Source code
│   ├── api/                 # API endpoints
│   │   ├── routes/          # API routes
│   │   └── app.py           # FastAPI application
│   ├── config/              # Configuration settings
│   ├── database/            # Database models and session management
│   ├── models/              # Pydantic schemas
│   ├── services/            # Business logic services
│   └── utils/               # Utility functions and classes
├── uploads/                 # Upload directory
│   └── images/              # Uploaded images
├── .env.example             # Example environment variables
├── Dockerfile               # Docker configuration
├── docker-compose.yml       # Docker Compose configuration
├── main.py                  # Application entry point
└── requirements.txt         # Python dependencies
```

## API Endpoints

### Upload API

- `POST /api/v1/upload` - Upload tree images with location data
- `GET /api/v1/upload/{upload_id}` - Get details of a specific upload
- `GET /api/v1/uploads/user/{user_id}` - List all uploads for a specific user

### Analysis API

- `POST /api/v1/analyze/{upload_id}` - Analyze tree images from a previously uploaded set
- `GET /api/v1/analysis/{analysis_id}` - Get details of a specific analysis
- `GET /api/v1/analyses/upload/{upload_id}` - Get analysis for a specific upload

### Certification API

- `POST /api/v1/certify/{analysis_id}` - Evaluate certification for a tree based on its analysis
- `GET /api/v1/certification/{certification_id}` - Get details of a specific certification
- `GET /api/v1/certifications/analysis/{analysis_id}` - Get certification for a specific analysis

## Setup Instructions

### Prerequisites

- Docker and Docker Compose
- Python 3.9+ (for local development)
- Gemma API key

### Environment Setup

1. Clone the repository
2. Copy `.env.example` to `.env` and update the values:
   ```
   cp .env.example .env
   ```
3. Update the `GEMMA_API_KEY` in the `.env` file

### Running with Docker

1. Build and start the containers:
   ```
   docker-compose up -d
   ```
2. Access the API at `http://localhost:8000`
3. API documentation is available at `http://localhost:8000/docs`

### Local Development

1. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the application:
   ```
   python main.py
   ```

## Testing

To run tests:

```
pytest
```