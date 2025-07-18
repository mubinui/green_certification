from fastapi import APIRouter, Depends, HTTPException, Body, Request
from typing import Dict, Any, List, Optional
import uuid
from sqlalchemy.orm import Session

from ...database.session import get_db
from ...services.certification_service import CertificationService
from ...models.schemas import CertificationResponse, RecommendationResponse


router = APIRouter()


@router.post("/certify/{analysis_id}", response_model=CertificationResponse)
async def certify_tree(
    analysis_id: str,
    db: Session = Depends(get_db)
):
    """
    Evaluate certification for a tree based on its analysis.
    
    Path parameters:
    - analysis_id: UUID of the analysis to evaluate
    """
    try:
        # Convert analysis_id to UUID
        try:
            analysis_id_uuid = uuid.UUID(analysis_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid analysis_id format")
        
        # Create certification service
        certification_service = CertificationService(db)
        
        # Evaluate certification
        result = await certification_service.evaluate_certification(analysis_id_uuid)
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Certification failed: {str(e)}")


@router.get("/certification/{certification_id}", response_model=CertificationResponse)
async def get_certification(
    certification_id: str,
    db: Session = Depends(get_db)
):
    """
    Get details of a specific certification by ID.
    """
    try:
        # Convert certification_id to UUID
        try:
            certification_id_uuid = uuid.UUID(certification_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid certification_id format")
        
        # Query the certification directly
        from ...database.models import Certification, Recommendation
        
        certification = db.query(Certification).filter(Certification.id == certification_id_uuid).first()
        
        if not certification:
            raise HTTPException(status_code=404, detail=f"Certification with ID {certification_id} not found")
        
        # Get recommendations for this certification
        recommendations = db.query(Recommendation).filter(
            Recommendation.certification_id == certification_id_uuid
        ).all()
        
        # Format recommendations
        formatted_recommendations = []
        for rec in recommendations:
            formatted_recommendations.append({
                "id": rec.id,
                "recommendation_type": rec.recommendation_type,
                "description": rec.description,
                "priority": rec.priority
            })
        
        # Format the response
        return {
            "id": certification.id,
            "analysis_id": certification.analysis_id,
            "environmental_score": certification.environmental_score,
            "species_score": certification.species_score,
            "geographic_suitability_score": certification.geographic_suitability_score,
            "proximity_score": certification.proximity_score,
            "overall_score": certification.overall_score,
            "certification_status": certification.certification_status.value,
            "certification_timestamp": certification.certification_timestamp,
            "expiration_date": certification.expiration_date,
            "recommendations": formatted_recommendations,
            "status": "completed"
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving certification: {str(e)}")


@router.get("/certifications/analysis/{analysis_id}", response_model=CertificationResponse)
async def get_analysis_certification(
    analysis_id: str,
    db: Session = Depends(get_db)
):
    """
    Get certification for a specific analysis.
    """
    try:
        # Convert analysis_id to UUID
        try:
            analysis_id_uuid = uuid.UUID(analysis_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid analysis_id format")
        
        # Query the certification for this analysis
        from ...database.models import Certification, Recommendation
        
        certification = db.query(Certification).filter(Certification.analysis_id == analysis_id_uuid).first()
        
        if not certification:
            raise HTTPException(status_code=404, detail=f"No certification found for analysis ID {analysis_id}")
        
        # Get recommendations for this certification
        recommendations = db.query(Recommendation).filter(
            Recommendation.certification_id == certification.id
        ).all()
        
        # Format recommendations
        formatted_recommendations = []
        for rec in recommendations:
            formatted_recommendations.append({
                "id": rec.id,
                "recommendation_type": rec.recommendation_type,
                "description": rec.description,
                "priority": rec.priority
            })
        
        # Format the response
        return {
            "id": certification.id,
            "analysis_id": certification.analysis_id,
            "environmental_score": certification.environmental_score,
            "species_score": certification.species_score,
            "geographic_suitability_score": certification.geographic_suitability_score,
            "proximity_score": certification.proximity_score,
            "overall_score": certification.overall_score,
            "certification_status": certification.certification_status.value,
            "certification_timestamp": certification.certification_timestamp,
            "expiration_date": certification.expiration_date,
            "recommendations": formatted_recommendations,
            "status": "completed"
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving certification: {str(e)}")