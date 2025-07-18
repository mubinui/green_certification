from fastapi import APIRouter, Depends, HTTPException, Body, Request
from typing import Dict, Any, List, Optional
import uuid
from sqlalchemy.orm import Session

from ...database.session import get_db
from ...services.tree_analyzer_service import TreeAnalyzerService
from ...models.schemas import AnalysisResponse


router = APIRouter()


@router.post("/analyze/{upload_id}", response_model=AnalysisResponse)
async def analyze_tree(
    upload_id: str,
    db: Session = Depends(get_db)
):
    """
    Analyze tree images from a previously uploaded set.
    
    Path parameters:
    - upload_id: UUID of the upload to analyze
    """
    try:
        # Convert upload_id to UUID
        try:
            upload_id_uuid = uuid.UUID(upload_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid upload_id format")
        
        # Create tree analyzer service
        tree_analyzer_service = TreeAnalyzerService(db)
        
        # Process the analysis
        result = await tree_analyzer_service.analyze_upload(upload_id_uuid)
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/analysis/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(
    analysis_id: str,
    db: Session = Depends(get_db)
):
    """
    Get details of a specific analysis by ID.
    """
    try:
        # Convert analysis_id to UUID
        try:
            analysis_id_uuid = uuid.UUID(analysis_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid analysis_id format")
        
        # Query the analysis directly from the database
        from ...database.models import Analysis
        
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id_uuid).first()
        
        if not analysis:
            raise HTTPException(status_code=404, detail=f"Analysis with ID {analysis_id} not found")
        
        # Format the response
        return {
            "id": analysis.id,
            "upload_id": analysis.upload_id,
            "species_common_name": analysis.species_common_name,
            "species_scientific_name": analysis.species_scientific_name,
            "species_confidence": analysis.species_confidence,
            "estimated_age": analysis.estimated_age,
            "age_confidence": analysis.age_confidence,
            "analysis_timestamp": analysis.analysis_timestamp,
            "model_version": analysis.model_version,
            "status": "completed"
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving analysis: {str(e)}")


@router.get("/analyses/upload/{upload_id}", response_model=AnalysisResponse)
async def get_upload_analysis(
    upload_id: str,
    db: Session = Depends(get_db)
):
    """
    Get analysis for a specific upload.
    """
    try:
        # Convert upload_id to UUID
        try:
            upload_id_uuid = uuid.UUID(upload_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid upload_id format")
        
        # Query the analysis for this upload
        from ...database.models import Analysis
        
        analysis = db.query(Analysis).filter(Analysis.upload_id == upload_id_uuid).first()
        
        if not analysis:
            raise HTTPException(status_code=404, detail=f"No analysis found for upload ID {upload_id}")
        
        # Format the response
        return {
            "id": analysis.id,
            "upload_id": analysis.upload_id,
            "species_common_name": analysis.species_common_name,
            "species_scientific_name": analysis.species_scientific_name,
            "species_confidence": analysis.species_confidence,
            "estimated_age": analysis.estimated_age,
            "age_confidence": analysis.age_confidence,
            "analysis_timestamp": analysis.analysis_timestamp,
            "model_version": analysis.model_version,
            "status": "completed"
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving analysis: {str(e)}")