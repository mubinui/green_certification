import requests
import json
from typing import Dict, Any, List, Optional, Union
from ..config import settings


class GemmaClient:
    """
    Client for interacting with the Gemma 3n LLM model via Ollama.
    Provides tree species identification and recommendation generation.
    """
    
    def __init__(self):
        self.api_url = settings.OLLAMA_API_URL
        self.model_name = settings.GEMMA_MODEL_NAME
    
    async def generate_completion(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a completion using the Gemma model.
        
        Args:
            prompt: The user prompt to send to the model
            system_prompt: Optional system prompt for context
            
        Returns:
            Dictionary containing the model's response
        """
        headers = {"Content-Type": "application/json"}
        
        data = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False
        }
        
        if system_prompt:
            data["system"] = system_prompt
        
        try:
            response = requests.post(f"{self.api_url}/generate", headers=headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            error_msg = f"Gemma API request failed: {str(e)}"
            if hasattr(e, "response") and e.response:
                error_msg += f", Status code: {e.response.status_code}, Response: {e.response.text}"
            raise RuntimeError(error_msg)
    
    async def identify_tree_species(self, image_features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Identify tree species from image features.
        
        Args:
            image_features: Dictionary of extracted image features
            
        Returns:
            Dictionary with species identification results
        """
        system_prompt = """
        You are a tree species identification expert. Your task is to identify tree species from image features.
        Provide scientific and common names with confidence scores. Only respond with JSON in the format:
        {
            "species_scientific_name": "Latin name",
            "species_common_name": "Common name",
            "confidence": 0.XX,
            "estimated_age": XX.X,
            "age_confidence": 0.XX
        }
        """
        
        prompt = f"""
        Based on these image features, identify the tree species:
        {json.dumps(image_features, indent=2)}
        
        Response should be only a valid JSON object with fields:
        - species_scientific_name: the scientific name of the tree species
        - species_common_name: the common name of the tree species
        - confidence: a value between 0.0 and 1.0 indicating your confidence in this identification
        - estimated_age: estimated age of the tree in years
        - age_confidence: a value between 0.0 and 1.0 indicating your confidence in the age estimation
        """
        
        try:
            response = await self.generate_completion(prompt, system_prompt)
            response_text = response.get('response', '{}')
            
            # Extract JSON from the response
            # First, find the first { and the last }
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}')
            
            if start_idx != -1 and end_idx != -1:
                json_str = response_text[start_idx:end_idx+1]
                result = json.loads(json_str)
                
                # Ensure all required fields are present
                required_fields = ["species_scientific_name", "species_common_name", "confidence"]
                if all(field in result for field in required_fields):
                    return result
                else:
                    missing = [field for field in required_fields if field not in result]
                    raise ValueError(f"Missing required fields in response: {missing}")
            else:
                raise ValueError("Could not find valid JSON in the response")
                
        except Exception as e:
            # Fallback to default values on error
            print(f"Species identification error: {str(e)}")
            return {
                "species_scientific_name": "Unknown",
                "species_common_name": "Unknown",
                "confidence": 0.0,
                "estimated_age": 0.0,
                "age_confidence": 0.0
            }
    
    async def generate_recommendations(self, analysis_data: Dict[str, Any], certification_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate recommendations based on tree analysis and certification data.
        
        Args:
            analysis_data: Dictionary containing tree analysis results
            certification_data: Dictionary containing certification results
            
        Returns:
            List of recommendation dictionaries
        """
        system_prompt = """
        You are a tree care and environmental expert. Your task is to generate recommendations for tree care
        and environmental improvement. Only respond with a JSON array of recommendations in the format:
        [
            {
                "recommendation_type": "care|environment|planting",
                "description": "Detailed description of the recommendation",
                "priority": 1-5 (1 being highest priority)
            }
        ]
        """
        
        prompt = f"""
        Based on this tree analysis and certification data, generate recommendations:
        
        Analysis:
        {json.dumps(analysis_data, indent=2)}
        
        Certification:
        {json.dumps(certification_data, indent=2)}
        
        Provide 2-5 recommendations in a JSON array with these fields for each recommendation:
        - recommendation_type: one of "care", "environment", or "planting"
        - description: a detailed, specific recommendation
        - priority: a number from 1 (highest priority) to 5 (lowest priority)
        """
        
        try:
            response = await self.generate_completion(prompt, system_prompt)
            response_text = response.get('response', '[]')
            
            # Extract JSON from the response
            start_idx = response_text.find('[')
            end_idx = response_text.rfind(']')
            
            if start_idx != -1 and end_idx != -1:
                json_str = response_text[start_idx:end_idx+1]
                result = json.loads(json_str)
                
                # Validate each recommendation
                valid_recommendations = []
                for rec in result:
                    if all(key in rec for key in ["recommendation_type", "description", "priority"]):
                        # Ensure priority is within range
                        rec["priority"] = max(1, min(5, rec["priority"]))
                        valid_recommendations.append(rec)
                
                return valid_recommendations
            else:
                raise ValueError("Could not find valid JSON array in the response")
                
        except Exception as e:
            # Fallback to default recommendations on error
            print(f"Recommendation generation error: {str(e)}")
            return [
                {
                    "recommendation_type": "care",
                    "description": "Regular watering and maintenance is recommended for optimal tree health.",
                    "priority": 1
                },
                {
                    "recommendation_type": "environment",
                    "description": "Consider adding mulch around the base of the tree to retain moisture and prevent weed growth.",
                    "priority": 2
                }
            ]