from fastapi import APIRouter, Depends, HTTPException, Body, Request
from typing import Dict, Any, List, Optional
import uuid
from sqlalchemy.orm import Session

from ...database.session import get_db
from ...services.upload_service import UploadService
from ...models.schemas import UploadCreate, UploadResponse, ImageBase


router = APIRouter()


@router.post("/upload", response_model=UploadResponse, status_code=201)
async def upload_tree_images(
    request: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """
    Upload tree images with location data for analysis.
    
    Request body should contain:
    - user_id: UUID of the user uploading the images
    - images: List of base64-encoded image data
    - latitude: Latitude of the tree location
    - longitude: Longitude of the tree location
    - description: Optional description of the tree
    """
    try:
        # Validate required fields
        if "user_id" not in request:
            raise HTTPException(status_code=400, detail="user_id is required")
        if "images" not in request or not request["images"]:
            raise HTTPException(status_code=400, detail="At least one image is required")
        if "latitude" not in request:
            raise HTTPException(status_code=400, detail="latitude is required")
        if "longitude" not in request:
            raise HTTPException(status_code=400, detail="longitude is required")
        
        # Get user_id as UUID
        try:
            user_id = uuid.UUID(request["user_id"])
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid user_id format")
        
        # Create upload service
        upload_service = UploadService(db)
        
        # Process the upload
        result = await upload_service.process_upload(
            user_id=user_id,
            image_data_list=request["images"],
            latitude=float(request["latitude"]),
            longitude=float(request["longitude"]),
            description=request.get("description")
        )
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/upload/{upload_id}", response_model=UploadResponse)
async def get_upload(
    upload_id: str,
    db: Session = Depends(get_db)
):
    """
    Get details of a specific upload by ID.
    """
    try:
        # Convert upload_id to UUID
        try:
            upload_id_uuid = uuid.UUID(upload_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid upload_id format")
        
        # Create upload service
        upload_service = UploadService(db)
        
        # Get the upload
        result = await upload_service.get_upload(upload_id_uuid)
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving upload: {str(e)}")


@router.get("/uploads/user/{user_id}", response_model=List[UploadResponse])
async def list_user_uploads(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    List all uploads for a specific user.
    """
    try:
        # Convert user_id to UUID
        try:
            user_id_uuid = uuid.UUID(user_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid user_id format")
        
        # Create upload service
        upload_service = UploadService(db)
        
        # List user uploads
        results = await upload_service.list_user_uploads(user_id_uuid)
        
        return results
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving uploads: {str(e)}")