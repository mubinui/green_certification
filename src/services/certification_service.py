import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from ..database import models
from ..utils.gemma_client import GemmaClient
from ..utils.geo_analyzer import GeoAnalyzer
from ..config import settings


class CertificationService:
    """
    Service for evaluating and certifying trees based on analysis data.
    Determines certification status and generates recommendations.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.gemma_client = GemmaClient()
        self.geo_analyzer = GeoAnalyzer()
    
    async def evaluate_certification(self, analysis_id: uuid.UUID) -> Dict[str, Any]:
        """
        Evaluate certification for a tree based on its analysis.
        
        Args:
            analysis_id: UUID of the analysis to evaluate
            
        Returns:
            Dictionary containing certification results
        """
        # Get analysis
        analysis = self.db.query(models.Analysis).filter(models.Analysis.id == analysis_id).first()
        
        if not analysis:
            raise ValueError(f"Analysis with ID {analysis_id} not found")
        
        # Get upload to access location data
        upload = self.db.query(models.Upload).filter(models.Upload.id == analysis.upload_id).first()
        
        if not upload:
            raise ValueError(f"Upload with ID {analysis.upload_id} not found")
        
        # Check if certification already exists
        existing_certification = self.db.query(models.Certification).filter(
            models.Certification.analysis_id == analysis_id
        ).first()
        
        if existing_certification:
            # Get recommendations for existing certification
            recommendations = self.db.query(models.Recommendation).filter(
                models.Recommendation.certification_id == existing_certification.id
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
            
            # Return existing certification
            return {
                "id": existing_certification.id,
                "analysis_id": existing_certification.analysis_id,
                "environmental_score": existing_certification.environmental_score,
                "species_score": existing_certification.species_score,
                "geographic_suitability_score": existing_certification.geographic_suitability_score,
                "proximity_score": existing_certification.proximity_score,
                "overall_score": existing_certification.overall_score,
                "certification_status": existing_certification.certification_status.value,
                "certification_timestamp": existing_certification.certification_timestamp,
                "expiration_date": existing_certification.expiration_date,
                "recommendations": formatted_recommendations,
                "status": "completed"
            }
        
        # Get tree species information
        tree_species = None
        if analysis.species_scientific_name and analysis.species_scientific_name != "Unknown":
            tree_species = self.db.query(models.TreeSpecies).filter(
                models.TreeSpecies.scientific_name == analysis.species_scientific_name
            ).first()
        
        # Calculate scores
        
        # 1. Environmental score
        environmental_score = 0.7  # Base score
        if tree_species:
            # Add bonus for fruit-bearing trees
            if tree_species.fruit_bearing:
                environmental_score += settings.FRUIT_TREE_SCORE_BONUS
            
            # Add neutral for crop trees
            if tree_species.type == models.SpeciesType.CROP:
                environmental_score += settings.CROP_TREE_SCORE_NEUTRAL
            
            # Add penalty for oxygen-absorbing trees
            if tree_species.type == models.SpeciesType.OXYGEN_ABSORBING:
                environmental_score += settings.OXYGEN_ABSORBING_PENALTY
        
        # Normalize to 0-1 range
        environmental_score = max(0.0, min(1.0, environmental_score))
        
        # 2. Species score (based on identification confidence)
        species_score = analysis.species_confidence or 0.5
        
        # 3. Geographic suitability score
        geo_rules = {}
        if tree_species:
            # Get geographic suitability rules for the species
            geo_rule = self.db.query(models.GeoSuitabilityRule).filter(
                models.GeoSuitabilityRule.species_scientific_name == tree_species.scientific_name
            ).first()
            
            if geo_rule:
                geo_rules = {
                    "min_latitude": geo_rule.min_latitude,
                    "max_latitude": geo_rule.max_latitude,
                    "min_longitude": geo_rule.min_longitude,
                    "max_longitude": geo_rule.max_longitude,
                    "min_elevation": geo_rule.min_elevation,
                    "max_elevation": geo_rule.max_elevation,
                    "soil_types": geo_rule.soil_types,
                    "climate_zones": geo_rule.climate_zones,
                    "precipitation_requirements": geo_rule.precipitation_requirements,
                    "temperature_requirements": geo_rule.temperature_requirements
                }
        
        # Evaluate geographic suitability
        geo_evaluation = self.geo_analyzer.evaluate_geographic_suitability(
            upload.latitude, 
            upload.longitude, 
            analysis.species_scientific_name or "Unknown",
            geo_rules
        )
        
        geographic_suitability_score = geo_evaluation.get("suitability_score", 0.8)
        
        # 4. Proximity score (check if there are other trees nearby)
        # In a real implementation, you would query nearby trees from the database
        # For this implementation, we'll use a mock proximity score
        proximity_score = 0.9  # Assume good spacing by default
        
        # Calculate overall score (weighted average of all scores)
        weights = {
            "environmental": 0.4,
            "species": 0.2,
            "geographic_suitability": 0.3,
            "proximity": 0.1
        }
        
        overall_score = (
            environmental_score * weights["environmental"] +
            species_score * weights["species"] +
            geographic_suitability_score * weights["geographic_suitability"] +
            proximity_score * weights["proximity"]
        )
        
        # Determine certification status
        certification_status = models.CertificationStatus.PENDING
        if overall_score >= 0.7:
            certification_status = models.CertificationStatus.CERTIFIED
        elif overall_score < 0.4:
            certification_status = models.CertificationStatus.REJECTED
        
        # Set expiration date (1 year from now)
        expiration_date = datetime.utcnow() + timedelta(days=365)
        
        # Create new certification record
        new_certification = models.Certification(
            id=uuid.uuid4(),
            analysis_id=analysis_id,
            environmental_score=environmental_score,
            species_score=species_score,
            geographic_suitability_score=geographic_suitability_score,
            proximity_score=proximity_score,
            overall_score=overall_score,
            certification_status=certification_status,
            certification_timestamp=datetime.utcnow(),
            expiration_date=expiration_date
        )
        
        # Save to database
        self.db.add(new_certification)
        self.db.commit()
        self.db.refresh(new_certification)
        
        # Generate recommendations
        analysis_data = {
            "species_common_name": analysis.species_common_name,
            "species_scientific_name": analysis.species_scientific_name,
            "species_confidence": analysis.species_confidence,
            "estimated_age": analysis.estimated_age,
            "location": {
                "latitude": upload.latitude,
                "longitude": upload.longitude
            }
        }
        
        certification_data = {
            "environmental_score": environmental_score,
            "species_score": species_score,
            "geographic_suitability_score": geographic_suitability_score,
            "proximity_score": proximity_score,
            "overall_score": overall_score,
            "certification_status": certification_status.value
        }
        
        recommendations_data = await self.gemma_client.generate_recommendations(
            analysis_data, certification_data
        )
        
        # Save recommendations
        saved_recommendations = []
        for rec_data in recommendations_data:
            recommendation = models.Recommendation(
                id=uuid.uuid4(),
                certification_id=new_certification.id,
                recommendation_type=rec_data.get("recommendation_type", "care"),
                description=rec_data.get("description", "No specific recommendation"),
                priority=rec_data.get("priority", 3)
            )
            
            self.db.add(recommendation)
            
            saved_recommendations.append({
                "id": recommendation.id,
                "recommendation_type": recommendation.recommendation_type,
                "description": recommendation.description,
                "priority": recommendation.priority
            })
        
        self.db.commit()
        
        # Return certification result
        return {
            "id": new_certification.id,
            "analysis_id": new_certification.analysis_id,
            "environmental_score": new_certification.environmental_score,
            "species_score": new_certification.species_score,
            "geographic_suitability_score": new_certification.geographic_suitability_score,
            "proximity_score": new_certification.proximity_score,
            "overall_score": new_certification.overall_score,
            "certification_status": new_certification.certification_status.value,
            "certification_timestamp": new_certification.certification_timestamp,
            "expiration_date": new_certification.expiration_date,
            "recommendations": saved_recommendations,
            "status": "completed"
        }