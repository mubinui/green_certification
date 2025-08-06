"""
Comprehensive API test with real tree image and Gemma model integration.
"""
import asyncio
import base64
import io
import json
import os
import requests
from PIL import Image
from pathlib import Path
from typing import Optional
import cv2
import numpy as np
import uuid


async def test_complete_api_workflow():
    """Test the complete API workflow with real tree image."""
    print("🌳 Green Certification - Complete API Workflow Test 🌳\n")
    
    # Use the downloaded tree image
    image_path = "test_images/oak_tree_1.jpg"
    if not os.path.exists(image_path):
        print("❌ Test image not found. Please run simple_test.py first to download images.")
        return
    
    print("✅ Using existing tree image:", image_path)
    
    # Load and convert image to base64
    with open(image_path, 'rb') as f:
        image_data = f.read()
    
    base64_image = base64.b64encode(image_data).decode('utf-8')
    print(f"✅ Image converted to base64 (size: {len(base64_image):,} chars)")
    
    # Test data
    user_id = str(uuid.uuid4())
    test_upload_data = {
        "user_id": user_id,
        "images": [base64_image],  # Single real tree image
        "latitude": 40.7128,
        "longitude": -74.0060,
        "description": "White Oak tree for certification testing"
    }
    
    print(f"📝 Test data prepared for user: {user_id}")
    print()
    
    # Test 1: Direct Gemma Model Test
    await test_direct_gemma_identification(image_path)
    
    # Test 2: API Upload Test (simulated)
    await test_api_simulation(test_upload_data)


async def test_direct_gemma_identification(image_path: str):
    """Test direct Gemma model identification with the tree image."""
    print("=" * 60)
    print("🤖 TESTING DIRECT GEMMA MODEL IDENTIFICATION")
    print("=" * 60)
    
    try:
        # Extract image features
        img = cv2.imread(image_path)
        if img is None:
            print("❌ Could not read image file")
            return
            
        height, width, channels = img.shape
        mean_bgr = cv2.mean(img)
        brightness = np.mean(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))
        
        # Enhanced image features
        image_features = {
            "image_dimensions": {"width": width, "height": height, "channels": channels},
            "file_size_bytes": os.path.getsize(image_path),
            "mean_colors": {
                "red": float(mean_bgr[2]),
                "green": float(mean_bgr[1]), 
                "blue": float(mean_bgr[0])
            },
            "brightness": float(brightness),
            "color_distribution": {
                "dominant_color": "green-brown" if mean_bgr[1] > mean_bgr[0] and mean_bgr[1] > mean_bgr[2] else "brown-green"
            },
            "description": "Tree image from forest environment, deciduous tree with visible trunk and foliage, natural lighting conditions"
        }
        
        print("🔍 Extracted image features:")
        print(json.dumps(image_features, indent=2))
        print()
        
        # Test with enhanced prompt
        ollama_url = "http://localhost:11434"
        model_name = "gemma3n:latest"
        
        system_prompt = """You are an expert botanist and tree species identification specialist. Based on the provided image analysis features, identify the most likely tree species. Consider:

1. Color patterns and distribution
2. Environmental context (forest setting)
3. Lighting conditions and brightness
4. Image dimensions and quality

Respond with ONLY a valid JSON object in this exact format:
{
    "species_scientific_name": "Genus species",
    "species_common_name": "Common name",
    "confidence": 0.85,
    "estimated_age": 15.5,
    "age_confidence": 0.70,
    "reasoning": "Detailed explanation of identification based on the features",
    "environmental_impact": {
        "oxygen_production": "high/medium/low",
        "carbon_sequestration": "high/medium/low", 
        "ecological_value": "high/medium/low"
    },
    "recommended_care": ["care tip 1", "care tip 2"]
}"""
        
        user_prompt = f"""Analyze this tree image data and identify the species:

IMAGE ANALYSIS RESULTS:
{json.dumps(image_features, indent=2)}

CONTEXT:
- This is a photograph of a tree in a natural forest environment
- The image shows good detail of trunk and foliage
- Natural lighting conditions
- Appears to be a mature deciduous tree

Based on these technical features and environmental context, provide your expert identification."""
        
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        headers = {"Content-Type": "application/json"}
        data = {
            "model": model_name,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,  # Lower temperature for more consistent results
                "top_p": 0.8
            }
        }
        
        print("🔄 Sending enhanced identification request to Gemma3n...")
        
        response = requests.post(f"{ollama_url}/api/generate", headers=headers, json=data, timeout=180)
        
        if response.status_code == 200:
            result = response.json()
            response_text = result.get("response", "")
            
            print("✅ Gemma3n Enhanced Response:")
            print("-" * 40)
            print(response_text)
            print("-" * 40)
            print()
            
            # Parse JSON response
            try:
                start_idx = response_text.find("{")
                end_idx = response_text.rfind("}") + 1
                
                if start_idx != -1 and end_idx > start_idx:
                    json_str = response_text[start_idx:end_idx]
                    parsed_result = json.loads(json_str)
                    
                    print("🌳 PARSED IDENTIFICATION RESULT:")
                    print("=" * 40)
                    print(json.dumps(parsed_result, indent=2))
                    print("=" * 40)
                    
                    # Validate required fields
                    required_fields = ["species_scientific_name", "species_common_name", "confidence"]
                    if all(field in parsed_result for field in required_fields):
                        print("✅ JSON response contains all required fields")
                        return parsed_result
                    else:
                        missing = [f for f in required_fields if f not in parsed_result]
                        print(f"⚠️ Missing required fields: {missing}")
                        return None
                else:
                    print("⚠️ Could not extract JSON from response")
                    return None
                    
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing error: {e}")
                print("Raw response text:")
                print(repr(response_text[:500]))
                return None
        else:
            print(f"❌ API request failed: HTTP {response.status_code}")
            print("Response:", response.text)
            return None
            
    except Exception as e:
        print(f"❌ Error in direct Gemma test: {e}")
        return None


async def test_api_simulation(upload_data: dict):
    """Simulate the API workflow without actually running the FastAPI server."""
    print("\n" + "=" * 60)
    print("🔗 SIMULATING API WORKFLOW")
    print("=" * 60)
    
    try:
        print("📤 Step 1: Upload Simulation")
        print(f"   User ID: {upload_data['user_id']}")
        print(f"   Images: {len(upload_data['images'])} image(s)")
        print(f"   Location: {upload_data['latitude']}, {upload_data['longitude']}")
        print(f"   Description: {upload_data['description']}")
        
        # Generate mock upload response
        upload_id = str(uuid.uuid4())
        upload_response = {
            "id": upload_id,
            "status": "completed",
            "upload_timestamp": "2025-08-06T12:00:00Z",
            "image_count": len(upload_data["images"])
        }
        print("✅ Upload simulation successful")
        print(f"   Upload ID: {upload_id}")
        print()
        
        print("🔍 Step 2: Analysis Simulation")
        # In a real scenario, this would call the tree analyzer service
        analysis_id = str(uuid.uuid4())
        
        # Use our actual Gemma model for the analysis
        image_path = "test_images/oak_tree_1.jpg"
        gemma_result = await test_direct_gemma_identification(image_path)
        
        if gemma_result:
            analysis_response = {
                "id": analysis_id,
                "upload_id": upload_id,
                "species_common_name": gemma_result.get("species_common_name"),
                "species_scientific_name": gemma_result.get("species_scientific_name"),
                "species_confidence": gemma_result.get("confidence"),
                "estimated_age": gemma_result.get("estimated_age"),
                "age_confidence": gemma_result.get("age_confidence"),
                "analysis_timestamp": "2025-08-06T12:05:00Z",
                "model_version": "gemma3n:latest"
            }
            print("✅ Analysis simulation successful using real Gemma model")
            print("📊 Analysis Results:")
            print(json.dumps(analysis_response, indent=2))
        else:
            print("❌ Analysis simulation failed - could not get Gemma result")
            return
        print()
        
        print("🏆 Step 3: Certification Simulation")
        certification_id = str(uuid.uuid4())
        
        # Mock certification logic based on species
        species_name = gemma_result.get("species_common_name", "").lower()
        scientific_name = gemma_result.get("species_scientific_name", "").lower()
        
        # Simple scoring logic
        if "oak" in species_name or "quercus" in scientific_name:
            environmental_score = 90.0  # Oak trees are excellent for environment
            species_score = 95.0
            geographic_score = 85.0  # Good for temperate regions
        else:
            environmental_score = 75.0
            species_score = 80.0
            geographic_score = 80.0
            
        proximity_score = 85.0  # Assume good spacing
        overall_score = (environmental_score + species_score + geographic_score + proximity_score) / 4
        
        certification_status = "certified" if overall_score >= 80 else "pending"
        
        certification_response = {
            "id": certification_id,
            "analysis_id": analysis_id,
            "environmental_score": environmental_score,
            "species_score": species_score,
            "geographic_suitability_score": geographic_score,
            "proximity_score": proximity_score,
            "overall_score": overall_score,
            "certification_status": certification_status,
            "certification_timestamp": "2025-08-06T12:10:00Z",
            "recommendations": [
                {
                    "id": str(uuid.uuid4()),
                    "recommendation_type": "maintenance",
                    "description": "Regular watering during dry seasons",
                    "priority": 2
                },
                {
                    "id": str(uuid.uuid4()),
                    "recommendation_type": "monitoring", 
                    "description": "Monitor for signs of disease or pest infestation",
                    "priority": 1
                }
            ]
        }
        
        print("✅ Certification simulation successful")
        print("🏆 Certification Results:")
        print(json.dumps(certification_response, indent=2))
        print()
        
        print("=" * 60)
        print("🎉 COMPLETE WORKFLOW TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Upload ID: {upload_id}")
        print(f"✅ Analysis ID: {analysis_id}")
        print(f"✅ Certification ID: {certification_id}")
        print(f"🌳 Species Identified: {gemma_result.get('species_common_name')} ({gemma_result.get('species_scientific_name')})")
        print(f"📊 Overall Score: {overall_score:.1f}/100")
        print(f"🏆 Status: {certification_status.upper()}")
        print(f"🤖 Model: gemma3n:latest")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error in API simulation: {e}")


async def test_with_multiple_images():
    """Test with multiple tree images if available."""
    print("\n" + "=" * 60)
    print("🌲 TESTING WITH MULTIPLE IMAGES")
    print("=" * 60)
    
    test_images_dir = Path("test_images")
    if not test_images_dir.exists():
        print("❌ test_images directory not found")
        return
        
    image_files = list(test_images_dir.glob("*.jpg"))
    if not image_files:
        print("❌ No image files found in test_images directory")
        return
        
    print(f"📁 Found {len(image_files)} image(s) to test:")
    for img in image_files:
        print(f"  - {img.name}")
    print()
    
    for image_file in image_files[:3]:  # Test up to 3 images
        print(f"🌳 Testing with: {image_file.name}")
        print("-" * 40)
        
        result = await test_direct_gemma_identification(str(image_file))
        if result:
            print(f"✅ {image_file.name}: {result.get('species_common_name')} (confidence: {result.get('confidence', 0)*100:.1f}%)")
        else:
            print(f"❌ {image_file.name}: Identification failed")
        print()


if __name__ == "__main__":
    asyncio.run(test_complete_api_workflow())
    # Uncomment to test with multiple images
    # asyncio.run(test_with_multiple_images())
