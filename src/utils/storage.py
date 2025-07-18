import os
import uuid
import base64
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime

from ..config import settings


class StorageManager:
    """
    Manages file storage operations for the Green Certification system.
    Supports local file system and can be extended to support cloud storage.
    """

    def __init__(self):
        self.storage_type = settings.STORAGE_TYPE
        self.storage_bucket = settings.STORAGE_BUCKET
        
        # Ensure local storage directory exists
        if self.storage_type == "local":
            os.makedirs(os.path.join(os.getcwd(), "storage", self.storage_bucket), exist_ok=True)

    def save_base64_image(self, base64_data: str, upload_id: str) -> Tuple[str, str, Dict[str, Any]]:
        """
        Decode and save a base64 encoded image.
        
        Args:
            base64_data: Base64 encoded image data
            upload_id: The UUID of the upload this image belongs to
            
        Returns:
            Tuple containing (file_url, file_type, metadata)
        """
        try:
            # Extract content type and image data
            if "," in base64_data:
                header, base64_data = base64_data.split(",", 1)
                # Extract content type from header (e.g., "data:image/jpeg;base64")
                content_type = header.split(";")[0].split(":")[1]
            else:
                # Assume JPEG if content type is not provided
                content_type = "image/jpeg"
            
            # Decode base64 image
            image_data = base64.b64decode(base64_data)
            
            # Generate filename with extension
            file_ext = self._get_extension_from_content_type(content_type)
            file_name = f"{upload_id}_{uuid.uuid4()}.{file_ext}"
            
            # Create path and save
            file_path = self._get_file_path(file_name)
            with open(file_path, "wb") as f:
                f.write(image_data)
            
            # Generate file URL
            file_url = self._get_file_url(file_name)
            
            # Generate metadata
            metadata = {
                "size": len(image_data),
                "uploaded_at": datetime.utcnow().isoformat(),
                "content_type": content_type
            }
            
            return file_url, content_type, metadata
        
        except Exception as e:
            # Log error
            print(f"Error saving image: {str(e)}")
            raise ValueError(f"Failed to save image: {str(e)}")

    def delete_image(self, image_url: str) -> bool:
        """
        Delete an image from storage.
        
        Args:
            image_url: The URL of the image to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            if self.storage_type == "local":
                file_name = os.path.basename(image_url)
                file_path = self._get_file_path(file_name)
                if os.path.exists(file_path):
                    os.remove(file_path)
                    return True
                return False
            elif self.storage_type == "s3":
                # Implement S3 deletion logic here
                # Will be implemented when S3 storage is required
                pass
            return False
        except Exception as e:
            # Log error
            print(f"Error deleting image: {str(e)}")
            return False

    def _get_file_path(self, file_name: str) -> str:
        """
        Get the physical file path for the given file name.
        
        Args:
            file_name: The name of the file
            
        Returns:
            The complete file path
        """
        if self.storage_type == "local":
            return os.path.join(os.getcwd(), "storage", self.storage_bucket, file_name)
        elif self.storage_type == "s3":
            # For S3, this would represent the object key
            return f"{self.storage_bucket}/{file_name}"
        else:
            return file_name

    def _get_file_url(self, file_name: str) -> str:
        """
        Get the URL for accessing the file.
        
        Args:
            file_name: The name of the file
            
        Returns:
            The URL to access the file
        """
        if self.storage_type == "local":
            return f"/storage/{self.storage_bucket}/{file_name}"
        elif self.storage_type == "s3":
            # This would be an S3 URL
            return f"https://{self.storage_bucket}.s3.amazonaws.com/{file_name}"
        else:
            return file_name

    def _get_extension_from_content_type(self, content_type: str) -> str:
        """
        Get file extension from content type.
        
        Args:
            content_type: The MIME type of the file
            
        Returns:
            The file extension
        """
        content_type_map = {
            "image/jpeg": "jpg",
            "image/png": "png",
            "image/tiff": "tiff"
        }
        
        return content_type_map.get(content_type.lower(), "jpg")