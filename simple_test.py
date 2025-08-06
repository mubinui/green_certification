"""
Simple test script to download tree images and test basic image processing.
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


async def download_tree_image(url: str, filename: str) -> Optional[str]:
    """Download a tree image from URL and save it locally."""
    try:
        print(f"Downloading image from: {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Create images directory if it doesn't exist
        images_dir = Path("test_images")
        images_dir.mkdir(exist_ok=True)
        
        # Save the image
        image_path = images_dir / filename
        with open(image_path, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ Image saved to: {image_path}")
        return str(image_path)
        
    except Exception as e:
        print(f"❌ Error downloading image: {e}")
        return None


def load_image_as_base64(image_path: str) -> Optional[str]:
    """Load an image and convert it to base64 string."""
    try:
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        # Convert to base64
        base64_string = base64.b64encode(image_data).decode('utf-8')
        return base64_string
        
    except Exception as e:
        print(f"❌ Error loading image: {e}")
        return None


def process_image_features(image_path: str) -> dict:
    """Extract basic features from an image for testing purposes."""
    try:
        # Read image with OpenCV
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError("Could not read image")
        
        # Basic image analysis
        height, width, channels = img.shape
        
        # Calculate mean colors (OpenCV uses BGR format)
        mean_bgr = cv2.mean(img)
        
        # Convert to RGB for better representation
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Calculate some basic features
        features = {
            "image_dimensions": {"width": width, "height": height, "channels": channels},
            "file_size_bytes": os.path.getsize(image_path),
            "mean_colors": {
                "red": float(mean_bgr[2]),    # BGR to RGB conversion
                "green": float(mean_bgr[1]),
                "blue": float(mean_bgr[0])
            },
            "brightness": float(np.mean(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))),
            "description": "Tree image processed for species identification"
        }
        
        return features
        
    except Exception as e:
        print(f"❌ Error processing image features: {e}")
        return {}


async def test_ollama_connection():
    """Test if Ollama is running and accessible."""
    print(f"\n=== Testing Ollama Connection ===")
    
    # Default Ollama settings
    ollama_url = "http://localhost:11434"
    model_name = "gemma:3n"
    
    print(f"Ollama API URL: {ollama_url}")
    print(f"Model name: {model_name}")
    
    try:
        # Test basic connection
        response = requests.get(f"{ollama_url}/api/tags", timeout=10)
        if response.status_code == 200:
            models = response.json()
            print("✅ Connected to Ollama successfully!")
            print("Available models:")
            for model in models.get('models', []):
                print(f"  - {model.get('name', 'Unknown')}")
            
            # Check if our model is available
            model_names = [model.get('name', '') for model in models.get('models', [])]
            if any(model_name in name for name in model_names):
                print(f"✅ {model_name} model is available")
                return True
            else:
                print(f"⚠️ {model_name} model not found. Available models listed above.")
                return False
        else:
            print(f"❌ Failed to connect to Ollama: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to Ollama at {ollama_url}")
        print("Make sure Ollama is installed and running:")
        print("1. Install Ollama: https://ollama.ai/")
        print("2. Run: ollama serve")
        print("3. Install model: ollama pull gemma:3n")
        return False
    except Exception as e:
        print(f"❌ Error connecting to Ollama: {e}")
        return False


async def test_gemma_with_simple_prompt():
    """Test Gemma model with a simple text prompt."""
    try:
        print("\n=== Testing Gemma Model with Simple Prompt ===")
        
        ollama_url = "http://localhost:11434"
        model_name = "gemma:3n"
        
        # Simple test prompt
        test_prompt = "What are the main characteristics to identify oak trees?"
        
        headers = {"Content-Type": "application/json"}
        data = {
            "model": model_name,
            "prompt": test_prompt,
            "stream": False
        }
        
        print(f"Sending prompt to Gemma: {test_prompt}")
        
        response = requests.post(
            f"{ollama_url}/api/generate", 
            headers=headers, 
            json=data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Gemma response:")
            print(f"Response: {result.get('response', 'No response')}")
            return True
        else:
            print(f"❌ Gemma request failed: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Gemma model: {e}")
        return False


async def test_gemma_species_identification(image_features: dict):
    """Test Gemma model for tree species identification."""
    try:
        print("\n=== Testing Gemma Model for Species Identification ===")
        
        ollama_url = "http://localhost:11434"
        model_name = "gemma:3n"
        
        # Create a detailed prompt for tree identification
        system_prompt = """You are a tree species identification expert. Based on the provided image features, identify the most likely tree species. Respond with only a valid JSON object in this exact format:
{
    "species_scientific_name": "Scientific name",
    "species_common_name": "Common name",
    "confidence": 0.85,
    "estimated_age": 15.5,
    "age_confidence": 0.70,
    "reasoning": "Brief explanation of identification"
}"""
        
        user_prompt = f"""Based on these image features, identify the tree species:
{json.dumps(image_features, indent=2)}

Please provide your identification as a JSON object only."""
        
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        headers = {"Content-Type": "application/json"}
        data = {
            "model": model_name,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9
            }
        }
        
        print("Sending species identification request to Gemma...")
        
        response = requests.post(
            f"{ollama_url}/api/generate", 
            headers=headers, 
            json=data,
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            response_text = result.get('response', '')
            
            print("✅ Gemma species identification response:")
            print(response_text)
            
            # Try to extract JSON from the response
            try:
                # Find JSON in response
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}')
                
                if start_idx != -1 and end_idx != -1:
                    json_str = response_text[start_idx:end_idx+1]
                    parsed_result = json.loads(json_str)
                    print("\n✅ Parsed identification result:")
                    print(json.dumps(parsed_result, indent=2))
                    return parsed_result
                else:
                    print("⚠️ Could not extract JSON from response")
                    return None
                    
            except json.JSONDecodeError as e:
                print(f"⚠️ Could not parse JSON response: {e}")
                return None
                
        else:
            print(f"❌ Species identification request failed: HTTP {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error in species identification: {e}")
        return None


async def main():
    """Main test function."""
    print("🌳 Green Certification - Tree Image & Gemma Model Test 🌳\n")
    
    # Test tree image URLs (free to use images)
    tree_image_urls = [
        {
            "url": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=500&h=500&fit=crop&auto=format",
            "filename": "oak_tree_1.jpg",
            "description": "Oak tree in forest"
        },
        {
            "url": "https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=500&h=500&fit=crop&auto=format", 
            "filename": "pine_tree_1.jpg",
            "description": "Pine tree"
        }
    ]
    
    # Test Ollama connection first
    ollama_available = await test_ollama_connection()
    
    if ollama_available:
        # Test simple prompt first
        await test_gemma_with_simple_prompt()
    
    # Download and test with tree images
    for image_info in tree_image_urls:
        print(f"\n{'='*60}")
        print(f"Testing with: {image_info['description']}")
        print(f"{'='*60}")
        
        # Download the image
        image_path = await download_tree_image(image_info["url"], image_info["filename"])
        
        if image_path and os.path.exists(image_path):
            # Show image info
            try:
                with Image.open(image_path) as img:
                    print(f"📸 Image info:")
                    print(f"  - Dimensions: {img.size}")
                    print(f"  - Format: {img.format}")
                    print(f"  - Mode: {img.mode}")
                    print(f"  - File size: {os.path.getsize(image_path):,} bytes")
            except Exception as e:
                print(f"❌ Error reading image info: {e}")
            
            # Process image features
            print("\n🔍 Extracting image features...")
            image_features = process_image_features(image_path)
            if image_features:
                print("✅ Image features extracted:")
                print(json.dumps(image_features, indent=2))
                
                # Convert to base64 for API testing
                base64_image = load_image_as_base64(image_path)
                if base64_image:
                    print(f"✅ Image converted to base64 (length: {len(base64_image):,} characters)")
                    
                    # Test with Gemma model if available
                    if ollama_available:
                        await test_gemma_species_identification(image_features)
                    else:
                        print("⏭️ Skipping Gemma model test (Ollama not available)")
                else:
                    print("❌ Failed to convert image to base64")
            else:
                print("❌ Failed to extract image features")
        else:
            print("❌ Failed to download image")
    
    print(f"\n{'='*60}")
    print("🎉 Test completed!")
    if os.path.exists("test_images"):
        images = list(Path("test_images").glob("*"))
        print(f"📁 Downloaded {len(images)} images to test_images/ directory")
        for img in images:
            print(f"  - {img.name}")
    print(f"{'='*60}")


if __name__ == "__main__":
    asyncio.run(main())
