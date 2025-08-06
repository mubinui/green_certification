"""
Test configuration and fixtures for the Green Certification API tests.
"""
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from uuid import uuid4, UUID
import base64
from PIL import Image
import io

from src.api.app import app
from src.database.models import Base
from src.database.session import get_db

# Test database URL
TEST_DATABASE_URL = "sqlite:///./test.db"

# Create test engine
engine = create_engine(
    TEST_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables for testing
Base.metadata.create_all(bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def sample_user_id():
    """Generate a sample user ID for testing."""
    return str(uuid4())


@pytest.fixture
def sample_upload_data():
    """Generate sample upload data with base64 encoded images."""
    # Create a small test image
    img = Image.new('RGB', (100, 100), color='green')
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='JPEG')
    img_buffer.seek(0)
    
    # Convert to base64
    img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
    
    return {
        "user_id": str(uuid4()),
        "images": [img_base64, img_base64, img_base64],
        "latitude": 40.7128,
        "longitude": -74.0060,
        "description": "Test tree in Central Park"
    }


@pytest.fixture
def sample_analysis_data():
    """Generate sample analysis result data."""
    return {
        "species_common_name": "Oak Tree",
        "species_scientific_name": "Quercus alba",
        "species_confidence": 0.92,
        "estimated_age": 15.5,
        "age_confidence": 0.78,
        "model_version": "gemma-3n-v1.0"
    }


@pytest.fixture
def sample_certification_data():
    """Generate sample certification result data."""
    return {
        "environmental_score": 85.5,
        "species_score": 90.0,
        "geographic_suitability_score": 88.2,
        "proximity_score": 75.0,
        "overall_score": 84.7,
        "certification_status": "certified"
    }


@pytest.fixture
def sample_coordinates():
    """Generate sample coordinate data for testing."""
    return {
        "valid_coordinates": [
            {"latitude": 40.7128, "longitude": -74.0060},  # New York
            {"latitude": 34.0522, "longitude": -118.2437},  # Los Angeles
            {"latitude": 51.5074, "longitude": -0.1278},  # London
        ],
        "invalid_coordinates": [
            {"latitude": 91.0, "longitude": 0.0},  # Invalid latitude
            {"latitude": 0.0, "longitude": 181.0},  # Invalid longitude
            {"latitude": -91.0, "longitude": 0.0},  # Invalid latitude
        ]
    }


def create_mock_user_in_db(db, user_id: UUID):
    """Create a mock user in the test database."""
    from src.database.models import User
    
    user = User(
        id=user_id,
        username=f"testuser_{str(user_id)[:8]}",
        email=f"test_{str(user_id)[:8]}@example.com",
        password_hash="hashed_password",
        organization="Test Organization"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
