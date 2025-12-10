"""
☁️ CLOUDINARY PRO - Advanced Cloudinary Integration
"""

import cloudinary
import cloudinary.uploader
import cloudinary.api
from cloudinary.utils import cloudinary_url
import os
from datetime import datetime
from typing import Dict, Optional
import base64
from io import BytesIO

class CloudinaryPro:
    def __init__(self):
        self.configured = False
        self.configure()
    
    def configure(self):
        """Configure Cloudinary"""
        try:
            cloudinary.config(
                cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
                api_key=os.getenv("CLOUDINARY_API_KEY"),
                api_secret=os.getenv("CLOUDINARY_API_SECRET"),
                secure=True
            )
            self.configured = True
            print("✅ Cloudinary configured successfully!")
        except Exception as e:
            print(f"❌ Cloudinary configuration error: {e}")
            self.configured = False
    
    def upload_image(self, image_data: bytes, public_id: str = None, folder: str = "master_bot") -> Dict:
        """Upload image to Cloudinary"""
        if not self.configured:
            return {}
        
        try:
            if public_id is None:
                public_id = f"image_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Upload image
            result = cloudinary.uploader.upload(
                image_data,
                public_id=public_id,
                folder=folder,
                overwrite=True,
                resource_type="image",
                transformation=[
                    {"quality": "auto:good"},
                    {"fetch_format": "auto"}
                ]
            )
            
            print(f"✅ Image uploaded: {result['secure_url']}")
            return result
            
        except Exception as e:
            print(f"❌ Error uploading image: {e}")
            return {}
    
    def upload_diagram(self, diagram_data: bytes, public_id: str = None, folder: str = "master_bot/diagrams") -> Dict:
        """Upload diagram to Cloudinary"""
        if not self.configured:
            return {}
        
        try:
            if public_id is None:
                public_id = f"diagram_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Upload diagram
            result = cloudinary.uploader.upload(
                diagram_data,
                public_id=public_id,
                folder=folder,
                overwrite=True,
                resource_type="image",
                transformation=[
                    {"quality": "auto:best"},
                    {"fetch_format": "png"}
                ]
            )
            
            print(f"✅ Diagram uploaded: {result['secure_url']}")
            return result
            
        except Exception as e:
            print(f"❌ Error uploading diagram: {e}")
            return {}
    
    def upload_base64_image(self, base64_string: str, public_id: str = None) -> Dict:
        """Upload base64 image to Cloudinary"""
        if not self.configured:
            return {}
        
        try:
            # Remove data URL prefix if present
            if base64_string.startswith('data:image'):
                base64_string = base64_string.split(',')[1]
            
            # Decode base64
            image_data = base64.b64decode(base64_string)
            
            # Upload
            return self.upload_image(image_data, public_id)
            
        except Exception as e:
            print(f"❌ Error uploading base64 image: {e}")
            return {}
    
    def generate_image_url(self, public_id: str, transformations: list = None) -> str:
        """Generate image URL with transformations"""
        if not self.configured:
            return ""
        
        try:
            if transformations is None:
                transformations = [
                    {"width": 800, "height": 600, "crop": "fill"},
                    {"quality": "auto"}
                ]
            
            url, options = cloudinary_url(
                public_id,
                transformation=transformations
            )
            
            return url
            
        except Exception as e:
            print(f"❌ Error generating image URL: {e}")
            return ""
    
    def delete_image(self, public_id: str):
        """Delete image from Cloudinary"""
        if not self.configured:
            return False
        
        try:
            result = cloudinary.uploader.destroy(public_id)
            return result.get('result') == 'ok'
            
        except Exception as e:
            print(f"❌ Error deleting image: {e}")
            return False
    
    def list_images(self, folder: str = "master_bot", max_results: int = 100):
        """List images in folder"""
        if not self.configured:
            return []
        
        try:
            result = cloudinary.api.resources(
                type="upload",
                prefix=folder,
                max_results=max_results,
                resource_type="image"
            )
            
            return result.get('resources', [])
            
        except Exception as e:
            print(f"❌ Error listing images: {e}")
            return []
    
    def create_image_thumbnail(self, image_url: str, width: int = 300, height: int = 200) -> str:
        """Create thumbnail from image URL"""
        if not self.configured:
            return image_url
        
        try:
            # Extract public_id from URL
            parts = image_url.split('/')
            public_id = parts[-1].split('.')[0]
            
            # Generate thumbnail URL
            thumb_url, _ = cloudinary_url(
                public_id,
                width=width,
                height=height,
                crop="fill",
                quality="auto"
            )
            
            return thumb_url
            
        except Exception as e:
            print(f"❌ Error creating thumbnail: {e}")
            return image_url
    
    def upload_file(self, file_path: str, public_id: str = None, folder: str = "master_bot/files"):
        """Upload any file to Cloudinary"""
        if not self.configured:
            return {}
        
        try:
            if public_id is None:
                public_id = os.path.basename(file_path).split('.')[0]
            
            result = cloudinary.uploader.upload(
                file_path,
                public_id=public_id,
                folder=folder,
                resource_type="auto"  # Auto-detect file type
            )
            
            print(f"✅ File uploaded: {result['secure_url']}")
            return result
            
        except Exception as e:
            print(f"❌ Error uploading file: {e}")
            return {}