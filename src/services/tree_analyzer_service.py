import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime

from sqlalchemy.orm import Session

from ..database import models
from ..utils.gemma_client import GemmaClient
from ..utils.image_processor import ImageProcessor


class TreeAnalyzerService:
    """
    Service for analyzing trees based on image data.
    Uses Gemma 3n model for species identification and analysis.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.gemma_client = GemmaClient()
        self.image_processor = ImageProcessor()
    
    async def analyze_upload(self, upload_id: uuid.UUID) -> Dict[str, Any]:
        """
        Analyze a tree upload using image data.
        
        Args:
            upload_id: UUID of the upload to analyze
            
        Returns:
            Dictionary containing analysis results
        """
        # Get upload with images
        upload = self.db.query(models.Upload).filter(models.Upload.id == upload_id).first()
        
        if not upload:
            raise ValueError(f"Upload with ID {upload_id} not found")
        
        # Get images for the upload
        images = self.db.query(models.Image).filter(models.Image.upload_id == upload_id).all()
        
        if not images:
            raise ValueError(f"No images found for upload with ID {upload_id}")
        
        # Check if analysis already exists
        existing_analysis = self.db.query(models.Analysis).filter(models.Analysis.upload_id == upload_id).first()
        
        if existing_analysis:
            return {
                "id": existing_analysis.id,
                "upload_id": existing_analysis.upload_id,
                "species_common_name": existing_analysis.species_common_name,
                "species_scientific_name": existing_analysis.species_scientific_name,
                "species_confidence": existing_analysis.species_confidence,
                "estimated_age": existing_analysis.estimated_age,
                "age_confidence": existing_analysis.age_confidence,
                "analysis_timestamp": existing_analysis.analysis_timestamp,
                "model_version": existing_analysis.model_version,
                "status": "completed"
            }
        
        # Update upload status to processing
        upload.status = models.UploadStatus.PROCESSING
        self.db.commit()
        
        try:
            # Process each image and collect features
            all_features = []
            
            for image in images:
                # This would typically load the image from storage and process it
                # For now, we'll just collect metadata as example features
                image_metadata = image.metadata or {}
                
                # In a real implementation, you would:
                # 1. Load the image from the image_url
                # 2. Use ImageProcessor to extract features
                # For this implementation, we'll use mock features
                mock_features = {
                    "image_id": str(image.id),
                    "image_type": image.image_type,
                    "avg_hue": 100.0,
                    "avg_saturation": 150.0,
                    "avg_value": 200.0,
                    "dominant_colors": [
                        {"r": 100, "g": 150, "b": 50},
                        {"r": 30, "g": 70, "b": 20},
                        {"r": 200, "g": 210, "b": 180}
                    ],
                    "sharpness": 85.5,
                    "height": image_metadata.get("height", 800),
                    "width": image_metadata.get("width", 600)
                }
                all_features.append(mock_features)
            
            # Combine features from all images
            combined_features = {
                "upload_id": str(upload_id),
                "image_count": len(images),
                "features": all_features,
                "location": {
                    "latitude": upload.latitude,
                    "longitude": upload.longitude
                }
            }
            
            # Use Gemma client to identify the tree species
            identification_result = await self.gemma_client.identify_tree_species(combined_features)
            
            # Create new analysis record
            new_analysis = models.Analysis(
                id=uuid.uuid4(),
                upload_id=upload_id,
                species_common_name=identification_result.get("species_common_name", "Unknown"),
                species_scientific_name=identification_result.get("species_scientific_name", "Unknown"),
                species_confidence=identification_result.get("confidence", 0.0),
                estimated_age=identification_result.get("estimated_age", 0.0),
                age_confidence=identification_result.get("age_confidence", 0.0),
                analysis_timestamp=datetime.utcnow(),
                model_version=self.gemma_client.model_name
            )
            
            # Save to database
            self.db.add(new_analysis)
            
            # Update upload status to completed
            upload.status = models.UploadStatus.COMPLETED
            self.db.commit()
            
            # Return analysis result
            return {
                "id": new_analysis.id,
                "upload_id": new_analysis.upload_id,
                "species_common_name": new_analysis.species_common_name,
                "species_scientific_name": new_analysis.species_scientific_name,
                "species_confidence": new_analysis.species_confidence,
                "estimated_age": new_analysis.estimated_age,
                "age_confidence": new_analysis.age_confidence,
                "analysis_timestamp": new_analysis.analysis_timestamp,
                "model_version": new_analysis.model_version,
                "status": "completed"
            }
        
        except Exception as e:
            # Update upload status to failed
            upload.status = models.UploadStatus.FAILED
            self.db.commit()
            
            # Re-raise the exception
            raise RuntimeError(f"Tree analysis failed: {str(e)}")
    
    async def get_tree_species_details(self, species_scientific_name: str) -> Dict[str, Any]:
        """
        Get details for a specific tree species.
        
        Args:
            species_scientific_name: Scientific name of the species to look up
            
        Returns:
            Dictionary containing species details
        """
        # Query the tree species from the database
        species = self.db.query(models.TreeSpecies).filter(
            models.TreeSpecies.scientific_name == species_scientific_name
        ).first()
        
        if species:
            # Return species details from database
            return {
                "id": species.id,
                "common_name": species.common_name,
                "scientific_name": species.scientific_name,
                "type": species.type.value,
                "oxygen_production": species.oxygen_production,
                "carbon_sequestration": species.carbon_sequestration,
                "fruit_bearing": species.fruit_bearing,
                "native_regions": species.native_regions
            }
        else:
            # If species not found, return basic details
            return {
                "scientific_name": species_scientific_name,
                "common_name": "Unknown",
                "type": "unknown",
                "note": "Species not found in database"
            }