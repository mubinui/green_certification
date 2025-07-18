from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, validator, root_validator
from enum import Enum


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


# Base models
class UserBase(BaseModel):
    username: str
    email: str
    organization: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserInDB(UserBase):
    id: UUID
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        orm_mode = True


class User(UserBase):
    id: UUID

    class Config:
        orm_mode = True


# Token schemas for authentication
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[UUID] = None


# Upload schemas
class ImageUpload(BaseModel):
    image_data: bytes
    image_type: str


class UploadBase(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    planting_date: Optional[datetime] = None
    additional_notes: Optional[str] = None


class UploadCreate(UploadBase):
    images: List[str] = Field(..., min_items=1, max_items=3)  # Base64 encoded images


class UploadInDB(UploadBase):
    id: UUID
    user_id: UUID
    upload_timestamp: datetime
    status: UploadStatus

    class Config:
        orm_mode = True


class UploadResponse(BaseModel):
    id: UUID
    status: UploadStatus
    upload_timestamp: datetime
    image_count: int

    class Config:
        orm_mode = True


# Image schemas
class ImageBase(BaseModel):
    image_url: str
    image_type: str


class ImageInDB(ImageBase):
    id: UUID
    upload_id: UUID
    upload_timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        orm_mode = True


class Image(ImageBase):
    id: UUID

    class Config:
        orm_mode = True


# Analysis schemas
class AnalysisBase(BaseModel):
    species_common_name: Optional[str] = None
    species_scientific_name: Optional[str] = None
    species_confidence: Optional[float] = Field(None, ge=0, le=1)
    estimated_age: Optional[float] = Field(None, gt=0)
    age_confidence: Optional[float] = Field(None, ge=0, le=1)
    model_version: Optional[str] = None


class AnalysisCreate(BaseModel):
    upload_id: UUID


class AnalysisInDB(AnalysisBase):
    id: UUID
    upload_id: UUID
    analysis_timestamp: datetime

    class Config:
        orm_mode = True


class AnalysisResponse(AnalysisBase):
    id: UUID
    analysis_timestamp: datetime
    upload_id: UUID

    class Config:
        orm_mode = True


# Certification schemas
class CertificationBase(BaseModel):
    environmental_score: Optional[float] = None
    species_score: Optional[float] = None
    geographic_suitability_score: Optional[float] = None
    proximity_score: Optional[float] = None
    overall_score: Optional[float] = None
    certification_status: CertificationStatus = CertificationStatus.PENDING


class CertificationCreate(BaseModel):
    analysis_id: UUID


class CertificationInDB(CertificationBase):
    id: UUID
    analysis_id: UUID
    certification_timestamp: datetime
    expiration_date: Optional[datetime] = None

    class Config:
        orm_mode = True


class CertificationResponse(CertificationBase):
    id: UUID
    certification_timestamp: datetime
    recommendations: List['RecommendationResponse'] = []

    class Config:
        orm_mode = True


# Recommendation schemas
class RecommendationBase(BaseModel):
    recommendation_type: str
    description: str
    priority: int = 0


class RecommendationInDB(RecommendationBase):
    id: UUID
    certification_id: UUID
    created_at: datetime

    class Config:
        orm_mode = True


class RecommendationResponse(RecommendationBase):
    id: UUID

    class Config:
        orm_mode = True


# Tree Species schemas
class TreeSpeciesBase(BaseModel):
    common_name: str
    scientific_name: str
    type: SpeciesType
    oxygen_production: Optional[float] = None
    carbon_sequestration: Optional[float] = None
    fruit_bearing: bool = False
    native_regions: Optional[List[str]] = None


class TreeSpeciesCreate(TreeSpeciesBase):
    pass


class TreeSpeciesInDB(TreeSpeciesBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class TreeSpecies(TreeSpeciesBase):
    id: UUID

    class Config:
        orm_mode = True


# Geo Suitability Rule schemas
class GeoSuitabilityRuleBase(BaseModel):
    species_scientific_name: str
    min_latitude: Optional[float] = None
    max_latitude: Optional[float] = None
    min_longitude: Optional[float] = None
    max_longitude: Optional[float] = None
    min_elevation: Optional[float] = None
    max_elevation: Optional[float] = None
    soil_types: Optional[List[str]] = None
    climate_zones: Optional[List[str]] = None
    precipitation_requirements: Optional[Dict[str, float]] = None
    temperature_requirements: Optional[Dict[str, float]] = None


class GeoSuitabilityRuleCreate(GeoSuitabilityRuleBase):
    pass


class GeoSuitabilityRuleInDB(GeoSuitabilityRuleBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class GeoSuitabilityRule(GeoSuitabilityRuleBase):
    id: UUID

    class Config:
        orm_mode = True


# Analysis request schema
class AnalysisRequest(BaseModel):
    upload_id: UUID


# Certification request schema
class CertificationRequest(BaseModel):
    analysis_id: UUID


# To solve the forward reference issue with CertificationResponse
CertificationResponse.update_forward_refs()