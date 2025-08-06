"""
Test script to download tree images and test the Gemma 3n model integration.
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

# Add the src directory to the path so we can import from it
import sys
sys.path.append(str(Path(__file__).parent / "src"))

from utils.gemma_client import GemmaClient
from utils.image_processor import ImageProcessor
from config.settings import settings


async def download_tree_image(url: str, filename: str) -> Optional[str]:
    """Download a tree image from URL and save it locally."""
    try:
        print(f"Downloading image from: {url}")
        response = requests.get(url)
        response.raise_for_status()
        
        # Create images directory if it doesn't exist
        images_dir = Path("test_images")
        images_dir.mkdir(exist_ok=True)
        
        # Save the image
        image_path = images_dir / filename
        with open(image_path, 'wb') as f:
            f.write(response.content)
        
        print(f"Image saved to: {image_path}")
        return str(image_path)
        
    except Exception as e:
        print(f"Error downloading image: {e}")
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
        print(f"Error loading image: {e}")
        return None


async def test_gemma_model_with_image(image_path: str):
    """Test the Gemma model with a tree image."""
    print(f"\n=== Testing Gemma Model with Image: {image_path} ===")
    
    try:
        # Initialize the image processor
        image_processor = ImageProcessor()
        
        # Process the image to extract features
        print("Processing image to extract features...")
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        # Convert to base64 for processing
        base64_image = base64.b64encode(image_data).decode('utf-8')
        
        # Decode the image using the image processor
        img_array, content_type = image_processor.decode_base64_image(base64_image)
        
        # Preprocess the image
        processed_img = image_processor.preprocess_image(img_array)
        
        # Extract basic features (mock implementation for testing)
        image_features = {
            "image_shape": list(processed_img.shape),
            "content_type": content_type,
            "mean_color": {
                "r": float(processed_img[:, :, 2].mean()),  # OpenCV uses BGR
                "g": float(processed_img[:, :, 1].mean()),
                "b": float(processed_img[:, :, 0].mean())
            },
            "image_size": os.path.getsize(image_path),
            "description": "Tree image for species identification"
        }
        
        print(f"Extracted features: {json.dumps(image_features, indent=2)}")
        
        # Initialize Gemma client
        gemma_client = GemmaClient()
        
        # Test species identification
        print("\nTesting species identification...")
        identification_result = await gemma_client.identify_tree_species(image_features)
        print(f"Species identification result:")
        print(json.dumps(identification_result, indent=2))
        
        return identification_result
        
    except Exception as e:
        print(f"Error testing Gemma model: {e}")
        return None


async def test_ollama_connection():
    """Test if Ollama is running and accessible."""
    print(f"\n=== Testing Ollama Connection ===")
    print(f"Ollama API URL: {settings.OLLAMA_API_URL}")
    print(f"Model name: {settings.GEMMA_MODEL_NAME}")
    
    try:
        # Test basic connection
        response = requests.get(f"{settings.OLLAMA_API_URL.replace('/api', '')}/api/tags")
        if response.status_code == 200:
            models = response.json()
            print("Available models:")
            for model in models.get('models', []):
                print(f"  - {model.get('name', 'Unknown')}")
            
            # Check if our model is available
            model_names = [model.get('name', '') for model in models.get('models', [])]
            if any(settings.GEMMA_MODEL_NAME in name for name in model_names):
                print(f"✅ {settings.GEMMA_MODEL_NAME} model is available")
                return True
            else:
                print(f"❌ {settings.GEMMA_MODEL_NAME} model not found")
                return False
        else:
            print(f"❌ Failed to connect to Ollama: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error connecting to Ollama: {e}")
        return False


async def main():
    """Main test function."""
    print("🌳 Green Certification - Gemma Model Test 🌳\n")
    
    # Test tree image URLs (free to use images)
    tree_image_urls = [
        {
            "url": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=500&h=500&fit=crop",
            "filename": "oak_tree_1.jpg",
            "description": "Oak tree in forest"
        },
        {
            "url": "https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=500&h=500&fit=crop", 
            "filename": "pine_tree_1.jpg",
            "description": "Pine tree"
        },
        {
            "url": "https://images.unsplash.com/photo-1502780402662-acc01917217e?w=500&h=500&fit=crop",
            "filename": "maple_tree_1.jpg", 
            "description": "Maple tree in autumn"
        }
    ]
    
    # Test Ollama connection first
    ollama_available = await test_ollama_connection()
    
    if not ollama_available:
        print("\n⚠️ Ollama is not available. Please start Ollama and install the Gemma model:")
        print("1. Install Ollama: https://ollama.ai/")
        print("2. Run: ollama pull gemma:3n")
        print("3. Start Ollama: ollama serve")
        print("\nContinuing with image download and processing tests...")
    
    # Download and test with tree images
    for image_info in tree_image_urls:
        print(f"\n{'='*60}")
        print(f"Testing with: {image_info['description']}")
        print(f"{'='*60}")
        
        # Download the image
        image_path = await download_tree_image(image_info["url"], image_info["filename"])
        
        if image_path and os.path.exists(image_path):
            print(f"✅ Image downloaded successfully: {image_path}")
            
            # Show image info
            try:
                with Image.open(image_path) as img:
                    print(f"Image dimensions: {img.size}")
                    print(f"Image format: {img.format}")
                    print(f"Image mode: {img.mode}")
            except Exception as e:
                print(f"Error reading image info: {e}")
            
            # Convert to base64 for API testing
            base64_image = load_image_as_base64(image_path)
            if base64_image:
                print(f"✅ Image converted to base64 (length: {len(base64_image)} characters)")
                
                # Test with Gemma model if available
                if ollama_available:
                    result = await test_gemma_model_with_image(image_path)
                    if result:
                        print("✅ Gemma model test completed successfully")
                    else:
                        print("❌ Gemma model test failed")
                else:
                    print("⏭️ Skipping Gemma model test (Ollama not available)")
            else:
                print("❌ Failed to convert image to base64")
        else:
            print("❌ Failed to download image")
    
    print(f"\n{'='*60}")
    print("🎉 Test completed! Check the test_images directory for downloaded images.")
    print(f"{'='*60}")


if __name__ == "__main__":
    asyncio.run(main())
