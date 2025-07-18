import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime

from sqlalchemy.orm import Session

from ..database import models
from ..utils.storage import StorageManager
from ..utils.image_processor import ImageProcessor
from ..config import settings


class UploadService:
    """
    Service for handling tree image uploads and metadata.
    Manages storage and preprocessing of uploaded images.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.storage_manager = StorageManager()
        self.image_processor = ImageProcessor()
    
    async def process_upload(
        self, 
        user_id: uuid.UUID, 
        image_data_list: List[str],
        latitude: float,
        longitude: float,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a new tree upload with images.
        
        Args:
            user_id: UUID of the user making the upload
            image_data_list: List of base64-encoded image data
            latitude: Latitude of the tree location
            longitude: Longitude of the tree location
            description: Optional description of the tree
            
        Returns:
            Dictionary containing upload details
        """
        # Check if the user exists
        user = self.db.query(models.User).filter(models.User.id == user_id).first()
        
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        # Create a new upload
        upload_id = uuid.uuid4()
        new_upload = models.Upload(
            id=upload_id,
            user_id=user_id,
            latitude=latitude,
            longitude=longitude,
            description=description,
            status=models.UploadStatus.PENDING,
            timestamp=datetime.utcnow()
        )
        
        # Save to database
        self.db.add(new_upload)
        self.db.commit()
        self.db.refresh(new_upload)
        
        # Process each image
        images = []
        
        for base64_data in image_data_list:
            try:
                # Save the image and get file URL
                file_url, content_type, metadata = await self.storage_manager.save_base64_image(
                    base64_data, 
                    str(upload_id)
                )
                
                # Create a new image record
                image_id = uuid.uuid4()
                new_image = models.Image(
                    id=image_id,
                    upload_id=upload_id,
                    image_url=file_url,
                    image_type=content_type,
                    metadata=metadata
                )
                
                # Add to database
                self.db.add(new_image)
                
                # Append to images list
                images.append({
                    "id": image_id,
                    "image_url": file_url,
                    "image_type": content_type,
                    "metadata": metadata
                })
                
            except Exception as e:
                # Log error
                print(f"Image processing error: {str(e)}")
                
                # Update upload status to failed
                new_upload.status = models.UploadStatus.FAILED
                self.db.commit()
                
                # Re-raise the exception
                raise RuntimeError(f"Image upload failed: {str(e)}")
        
        # Update upload status to uploaded
        new_upload.status = models.UploadStatus.UPLOADED
        self.db.commit()
        
        # Return upload details
        return {
            "id": upload_id,
            "user_id": user_id,
            "latitude": latitude,
            "longitude": longitude,
            "description": description,
            "status": models.UploadStatus.UPLOADED.value,
            "timestamp": new_upload.timestamp,
            "images": images
        }
    
    async def get_upload(self, upload_id: uuid.UUID) -> Dict[str, Any]:
        """
        Get upload details by ID.
        
        Args:
            upload_id: UUID of the upload to retrieve
            
        Returns:
            Dictionary containing upload details
        """
        # Get upload
        upload = self.db.query(models.Upload).filter(models.Upload.id == upload_id).first()
        
        if not upload:
            raise ValueError(f"Upload with ID {upload_id} not found")
        
        # Get images for the upload
        images = self.db.query(models.Image).filter(models.Image.upload_id == upload_id).all()
        
        # Format images
        formatted_images = []
        for image in images:
            formatted_images.append({
                "id": image.id,
                "image_url": image.image_url,
                "image_type": image.image_type,
                "metadata": image.metadata
            })
        
        # Return upload details
        return {
            "id": upload.id,
            "user_id": upload.user_id,
            "latitude": upload.latitude,
            "longitude": upload.longitude,
            "description": upload.description,
            "status": upload.status.value,
            "timestamp": upload.timestamp,
            "images": formatted_images
        }
    
    async def list_user_uploads(self, user_id: uuid.UUID) -> List[Dict[str, Any]]:
        """
        List all uploads for a user.
        
        Args:
            user_id: UUID of the user
            
        Returns:
            List of upload dictionaries
        """
        # Get all uploads for the user
        uploads = self.db.query(models.Upload).filter(models.Upload.user_id == user_id).all()
        
        # Format uploads
        formatted_uploads = []
        for upload in uploads:
            formatted_uploads.append({
                "id": upload.id,
                "user_id": upload.user_id,
                "latitude": upload.latitude,
                "longitude": upload.longitude,
                "description": upload.description,
                "status": upload.status.value,
                "timestamp": upload.timestamp
            })
        
        return formatted_uploads