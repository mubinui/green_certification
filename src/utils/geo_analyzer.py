import math
from typing import Dict, Any, List, Optional, Tuple
import requests
import json
import os
from ..config import settings


class GeoAnalyzer:
    """
    Analyzes geographic data for the Green Duty system.
    Provides utilities for evaluating geographic suitability and proximity.
    """
    
    def __init__(self):
        self.geo_data_path = settings.GEO_DATA_PATH
        self.proximity_radius = settings.DEFAULT_PROXIMITY_RADIUS
        
        # Ensure geo data directory exists
        os.makedirs(self.geo_data_path, exist_ok=True)

    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate the Haversine distance between two points on Earth.
        
        Args:
            lat1: Latitude of first point in degrees
            lon1: Longitude of first point in degrees
            lat2: Latitude of second point in degrees
            lon2: Longitude of second point in degrees
            
        Returns:
            Distance between the points in meters
        """
        # Convert coordinates from degrees to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # Earth radius in meters
        earth_radius = 6371000
        
        # Haversine formula
        d_lat = lat2_rad - lat1_rad
        d_lon = lon2_rad - lon1_rad
        a = math.sin(d_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(d_lon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        # Distance in meters
        distance = earth_radius * c
        
        return distance

    def check_proximity_to_existing_trees(
        self, 
        latitude: float, 
        longitude: float, 
        trees_locations: List[Dict[str, float]],
        radius: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Check if the new tree is close to existing trees.
        
        Args:
            latitude: Latitude of the new tree
            longitude: Longitude of the new tree
            trees_locations: List of dictionaries containing latitude and longitude of existing trees
            radius: Maximum distance to consider as proximate (in meters)
            
        Returns:
            Dictionary with proximity analysis results
        """
        if radius is None:
            radius = self.proximity_radius
            
        nearby_trees = []
        min_distance = float('inf')
        
        for tree in trees_locations:
            distance = self.calculate_distance(
                latitude, longitude, 
                tree["latitude"], tree["longitude"]
            )
            
            if distance <= radius:
                nearby_trees.append({
                    "latitude": tree["latitude"],
                    "longitude": tree["longitude"],
                    "distance": distance
                })
                
                if distance < min_distance:
                    min_distance = distance
        
        return {
            "nearby_count": len(nearby_trees),
            "nearby_trees": nearby_trees,
            "min_distance": min_distance if nearby_trees else None,
            "is_isolated": len(nearby_trees) == 0
        }
    
    def evaluate_geographic_suitability(
        self, 
        latitude: float, 
        longitude: float, 
        species_scientific_name: str,
        geo_rules: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluate the geographic suitability of the location for the given tree species.
        
        Args:
            latitude: Latitude of the tree
            longitude: Longitude of the tree
            species_scientific_name: Scientific name of the tree species
            geo_rules: Dictionary containing geographic suitability rules for the species
            
        Returns:
            Dictionary with suitability evaluation results
        """
        evaluation = {
            "is_suitable": True,
            "factors": [],
            "suitability_score": 1.0,
            "details": {}
        }
        
        # Check latitude range
        if geo_rules.get("min_latitude") is not None and latitude < geo_rules["min_latitude"]:
            evaluation["is_suitable"] = False
            evaluation["factors"].append("latitude_too_low")
            evaluation["details"]["latitude"] = {
                "current": latitude,
                "min_required": geo_rules["min_latitude"]
            }
        
        if geo_rules.get("max_latitude") is not None and latitude > geo_rules["max_latitude"]:
            evaluation["is_suitable"] = False
            evaluation["factors"].append("latitude_too_high")
            evaluation["details"]["latitude"] = {
                "current": latitude,
                "max_allowed": geo_rules["max_latitude"]
            }
        
        # Check longitude range
        if geo_rules.get("min_longitude") is not None and longitude < geo_rules["min_longitude"]:
            evaluation["is_suitable"] = False
            evaluation["factors"].append("longitude_too_low")
            evaluation["details"]["longitude"] = {
                "current": longitude,
                "min_required": geo_rules["min_longitude"]
            }
        
        if geo_rules.get("max_longitude") is not None and longitude > geo_rules["max_longitude"]:
            evaluation["is_suitable"] = False
            evaluation["factors"].append("longitude_too_high")
            evaluation["details"]["longitude"] = {
                "current": longitude,
                "max_allowed": geo_rules["max_longitude"]
            }
        
        # Calculate elevation if not provided in the rules (could be implemented with an external API)
        # For now, we assume elevation is appropriate if not specified in rules
        
        # Calculate suitability score based on factors
        factor_count = len(evaluation["factors"])
        if factor_count > 0:
            evaluation["suitability_score"] = max(0.0, 1.0 - (factor_count * 0.2))
        
        return evaluation

    def get_climate_data(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """
        Get climate data for the given location.
        This is a placeholder function that would typically use an external API.
        
        Args:
            latitude: Latitude of the location
            longitude: Longitude of the location
            
        Returns:
            Dictionary with climate data
        """
        # This is a placeholder that would typically call an external weather API
        # For now, return mock data
        return {
            "temperature": {
                "annual_mean": 15.0,
                "min_monthly_mean": 5.0,
                "max_monthly_mean": 25.0
            },
            "precipitation": {
                "annual_mean": 900.0,
                "min_monthly_mean": 40.0,
                "max_monthly_mean": 120.0
            },
            "climate_zone": "temperate",
            "soil_type": "loam"
        }