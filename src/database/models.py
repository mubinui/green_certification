import uuid
from datetime import datetime
from typing import List, Dict, Optional
from enum import Enum
from sqlalchemy import Column, String, Float, Boolean, DateTime, ForeignKey, Integer, JSON, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from geoalchemy2 import Geography

Base = declarative_base()


class UploadStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class CertificationStatus(str, Enum):
    PENDING = "pending"
    CERTIFIED = "certified"
    REJECTED = "rejected"
    EXPIRED = "expired"


class SpeciesType(str, Enum):
    FRUIT = "fruit"
    CROP = "crop"
    DECORATIVE = "decorative"
    TIMBER = "timber"
    OXYGEN_ABSORBING = "oxygen_absorbing"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    organization = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_login = Column(DateTime)

    # Relationships
    uploads = relationship("Upload", back_populates="user")


class Upload(Base):
    __tablename__ = "uploads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    location = Column(Geography(geometry_type='POINT', srid=4326), nullable=False)  # PostGIS Point
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    planting_date = Column(DateTime)
    upload_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    additional_notes = Column(String)
    status = Column(SQLEnum(UploadStatus), default=UploadStatus.PENDING, nullable=False)

    # Relationships
    user = relationship("User", back_populates="uploads")
    images = relationship("Image", back_populates="upload", cascade="all, delete-orphan")
    analysis = relationship("Analysis", back_populates="upload", uselist=False)


class Image(Base):
    __tablename__ = "images"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    upload_id = Column(UUID(as_uuid=True), ForeignKey("uploads.id"), nullable=False)
    image_url = Column(String, nullable=False)
    image_type = Column(String, nullable=False)
    upload_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    metadata = Column(JSON)

    # Relationships
    upload = relationship("Upload", back_populates="images")


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    upload_id = Column(UUID(as_uuid=True), ForeignKey("uploads.id"), unique=True, nullable=False)
    species_common_name = Column(String)
    species_scientific_name = Column(String)
    species_confidence = Column(Float)
    estimated_age = Column(Float)
    age_confidence = Column(Float)
    analysis_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    model_version = Column(String)

    # Relationships
    upload = relationship("Upload", back_populates="analysis")
    certification = relationship("Certification", back_populates="analysis", uselist=False)


class Certification(Base):
    __tablename__ = "certifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("analyses.id"), unique=True, nullable=False)
    environmental_score = Column(Float)
    species_score = Column(Float)
    geographic_suitability_score = Column(Float)
    proximity_score = Column(Float)
    overall_score = Column(Float)
    certification_status = Column(SQLEnum(CertificationStatus), default=CertificationStatus.PENDING, nullable=False)
    certification_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    expiration_date = Column(DateTime)

    # Relationships
    analysis = relationship("Analysis", back_populates="certification")
    recommendations = relationship("Recommendation", back_populates="certification", cascade="all, delete-orphan")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    certification_id = Column(UUID(as_uuid=True), ForeignKey("certifications.id"), nullable=False)
    recommendation_type = Column(String, nullable=False)
    description = Column(String, nullable=False)
    priority = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    certification = relationship("Certification", back_populates="recommendations")


class TreeSpecies(Base):
    __tablename__ = "tree_species"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    common_name = Column(String, nullable=False)
    scientific_name = Column(String, nullable=False, unique=True)
    type = Column(SQLEnum(SpeciesType), nullable=False)
    oxygen_production = Column(Float)  # Positive value for oxygen production
    carbon_sequestration = Column(Float)
    fruit_bearing = Column(Boolean, default=False)
    native_regions = Column(JSON)  # List of region codes
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class GeoSuitabilityRule(Base):
    __tablename__ = "geo_suitability_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    species_scientific_name = Column(String, ForeignKey("tree_species.scientific_name"), nullable=False)
    min_latitude = Column(Float)
    max_latitude = Column(Float)
    min_longitude = Column(Float)
    max_longitude = Column(Float)
    min_elevation = Column(Float)
    max_elevation = Column(Float)
    soil_types = Column(JSON)  # List of suitable soil types
    climate_zones = Column(JSON)  # List of suitable climate zones
    precipitation_requirements = Column(JSON)  # Dict with min/max values
    temperature_requirements = Column(JSON)  # Dict with min/max values
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)