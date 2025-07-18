import cv2
import numpy as np
import base64
from typing import Dict, Any, List, Optional, Tuple
from PIL import Image
import io


class ImageProcessor:
    """
    Processes images for the Green Certification system.
    Provides utilities for preprocessing images before tree analysis.
    """

    @staticmethod
    def decode_base64_image(base64_data: str) -> Tuple[np.ndarray, str]:
        """
        Decode a base64 encoded image to a numpy array.
        
        Args:
            base64_data: Base64 encoded image data
            
        Returns:
            Tuple containing (numpy array, content type)
        """
        try:
            # Extract content type and image data
            if "," in base64_data:
                header, base64_data = base64_data.split(",", 1)
                content_type = header.split(";")[0].split(":")[1]
            else:
                content_type = "image/jpeg"
            
            # Decode base64 image
            img_data = base64.b64decode(base64_data)
            
            # Convert to numpy array
            nparr = np.frombuffer(img_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            return img, content_type
        except Exception as e:
            raise ValueError(f"Failed to decode image: {str(e)}")

    @staticmethod
    def preprocess_image(image: np.ndarray, target_size: Tuple[int, int] = (512, 512)) -> np.ndarray:
        """
        Preprocess image for the tree analysis model.
        
        Args:
            image: Input image as numpy array
            target_size: Target size to resize image to
            
        Returns:
            Preprocessed image as numpy array
        """
        try:
            # Resize the image
            resized = cv2.resize(image, target_size)
            
            # Convert to RGB if in BGR (OpenCV default)
            if len(image.shape) == 3 and image.shape[2] == 3:
                resized = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
            
            # Normalize pixel values to [0, 1]
            normalized = resized.astype(np.float32) / 255.0
            
            return normalized
        except Exception as e:
            raise ValueError(f"Failed to preprocess image: {str(e)}")

    @staticmethod
    def enhance_image_quality(image: np.ndarray) -> np.ndarray:
        """
        Enhance image quality for better analysis.
        
        Args:
            image: Input image as numpy array
            
        Returns:
            Enhanced image as numpy array
        """
        try:
            # Convert to Lab color space
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            
            # Split channels
            l, a, b = cv2.split(lab)
            
            # Apply CLAHE to L channel
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            cl = clahe.apply(l)
            
            # Merge channels
            enhanced_lab = cv2.merge((cl, a, b))
            
            # Convert back to BGR
            enhanced_image = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
            
            return enhanced_image
        except Exception as e:
            # If enhancement fails, return the original image
            print(f"Image enhancement failed: {str(e)}")
            return image

    @staticmethod
    def extract_image_features(image: np.ndarray) -> Dict[str, Any]:
        """
        Extract features from the image that might be useful for tree analysis.
        
        Args:
            image: Input image as numpy array
            
        Returns:
            Dictionary of extracted features
        """
        features = {}
        
        try:
            # Convert to HSV for color analysis
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Calculate average hue, saturation, and value
            h, s, v = cv2.split(hsv)
            features["avg_hue"] = float(np.mean(h))
            features["avg_saturation"] = float(np.mean(s))
            features["avg_value"] = float(np.mean(v))
            
            # Calculate dominant colors using K-means
            pixels = hsv.reshape(-1, 3)
            pixels = np.float32(pixels)
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
            k = 3  # Extract 3 dominant colors
            _, labels, centers = cv2.kmeans(pixels, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
            
            # Convert back to BGR for easier interpretation
            centers = np.uint8(centers)
            centers_bgr = cv2.cvtColor(centers.reshape(1, k, 3), cv2.COLOR_HSV2BGR).reshape(k, 3)
            
            # Add dominant colors to features
            features["dominant_colors"] = [
                {"b": int(centers_bgr[i][0]), "g": int(centers_bgr[i][1]), "r": int(centers_bgr[i][2])}
                for i in range(k)
            ]
            
            # Calculate image sharpness
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            features["sharpness"] = float(laplacian_var)
            
            # Calculate image dimensions
            features["height"] = int(image.shape[0])
            features["width"] = int(image.shape[1])
            features["aspect_ratio"] = float(image.shape[1]) / float(image.shape[0])
            
        except Exception as e:
            print(f"Feature extraction error: {str(e)}")
        
        return features