import os
import uuid
import mimetypes
from datetime import datetime
from typing import Optional, Dict, Any, List
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from django.utils import timezone
from storage_backends import get_storage_backend
import logging

logger = logging.getLogger(__name__)


class MediaManager:
    """Centralized media management service for handling file uploads, processing, and storage."""
    
    def __init__(self):
        self.storage_backend = get_storage_backend()
        self.supported_image_formats = ['JPEG', 'PNG', 'WEBP', 'BMP']
        self.supported_video_formats = ['mp4', 'mov', 'avi', 'mkv', 'webm']
        self.max_image_size = (4096, 4096)  # Max dimensions
        self.max_file_size = 100 * 1024 * 1024  # 100MB
    
    def validate_file(self, file) -> Dict[str, Any]:
        """Validate uploaded file for size, format, and security."""
        validation_result = {
            'is_valid': True,
            'errors': [],
            'file_info': {}
        }
        
        try:
            # Check file size
            if file.size > self.max_file_size:
                validation_result['is_valid'] = False
                validation_result['errors'].append(f'File size exceeds maximum limit of {self.max_file_size / (1024*1024):.1f}MB')
            
            # Get file info
            file_extension = os.path.splitext(file.name)[1].lower().lstrip('.')
            mime_type, _ = mimetypes.guess_type(file.name)
            
            validation_result['file_info'] = {
                'name': file.name,
                'size': file.size,
                'extension': file_extension,
                'mime_type': mime_type,
                'is_image': mime_type and mime_type.startswith('image/'),
                'is_video': mime_type and mime_type.startswith('video/')
            }
            
            # Validate file type
            if validation_result['file_info']['is_image']:
                if file_extension not in ['jpg', 'jpeg', 'png', 'webp', 'bmp']:
                    validation_result['is_valid'] = False
                    validation_result['errors'].append(f'Unsupported image format: {file_extension}')
            elif validation_result['file_info']['is_video']:
                if file_extension not in self.supported_video_formats:
                    validation_result['is_valid'] = False
                    validation_result['errors'].append(f'Unsupported video format: {file_extension}')
            else:
                validation_result['is_valid'] = False
                validation_result['errors'].append('File must be an image or video')
            
            # Additional image validation
            if validation_result['file_info']['is_image'] and validation_result['is_valid']:
                try:
                    with Image.open(file) as img:
                        width, height = img.size
                        validation_result['file_info']['width'] = width
                        validation_result['file_info']['height'] = height
                        
                        if width > self.max_image_size[0] or height > self.max_image_size[1]:
                            validation_result['is_valid'] = False
                            validation_result['errors'].append(f'Image dimensions exceed maximum size of {self.max_image_size[0]}x{self.max_image_size[1]}')
                        
                        # Reset file pointer
                        file.seek(0)
                except Exception as e:
                    validation_result['is_valid'] = False
                    validation_result['errors'].append(f'Invalid image file: {str(e)}')
            
        except Exception as e:
            validation_result['is_valid'] = False
            validation_result['errors'].append(f'File validation error: {str(e)}')
            logger.error(f'File validation error: {str(e)}')
        
        return validation_result
    
    def generate_file_path(self, file_name: str, event_id: Optional[str] = None, file_type: str = 'media') -> str:
        """Generate a unique file path for storage."""
        file_extension = os.path.splitext(file_name)[1].lower()
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # Create path structure: year/month/event_id/file_type/filename
        now = datetime.now()
        path_parts = [
            str(now.year),
            f"{now.month:02d}",
        ]
        
        if event_id:
            path_parts.append(str(event_id))
        
        path_parts.extend([file_type, unique_filename])
        
        return '/'.join(path_parts)
    
    def add_watermark(self, image: Image.Image) -> Image.Image:
        """Add watermark to image if enabled in settings."""
        if not getattr(settings, 'WATERMARK_ENABLED', False):
            return image
        
        try:
            # Create a copy to avoid modifying original
            watermarked = image.copy()
            
            # Create watermark
            watermark_text = getattr(settings, 'WATERMARK_TEXT', 'Eddits by Meet Dudhwala')
            opacity = int(getattr(settings, 'WATERMARK_OPACITY', 0.3) * 255)
            
            # Create transparent overlay
            overlay = Image.new('RGBA', watermarked.size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(overlay)
            
            # Calculate font size based on image size
            font_size = max(20, min(watermarked.width, watermarked.height) // 20)
            
            try:
                # Try to use a nice font
                font = ImageFont.truetype('arial.ttf', font_size)
            except:
                # Fallback to default font
                font = ImageFont.load_default()
            
            # Get text dimensions
            bbox = draw.textbbox((0, 0), watermark_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Position watermark in bottom right corner
            margin = 20
            x = watermarked.width - text_width - margin
            y = watermarked.height - text_height - margin
            
            # Draw watermark
            draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255, opacity))
            
            # Composite the watermark onto the image
            watermarked = Image.alpha_composite(watermarked.convert('RGBA'), overlay)
            
            # Convert back to original mode if needed
            if image.mode != 'RGBA':
                watermarked = watermarked.convert(image.mode)
            
            return watermarked
            
        except Exception as e:
            logger.error(f'Error adding watermark: {str(e)}')
            return image
    
    def process_image(self, file, add_watermark: bool = True) -> Dict[str, Any]:
        """Process image file - resize, optimize, add watermark if needed."""
        try:
            with Image.open(file) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    # Create white background for transparency
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                
                # Get original dimensions
                original_width, original_height = img.size
                
                # Add watermark if enabled
                if add_watermark:
                    img = self.add_watermark(img)
                
                # Optimize image
                img = img.convert('RGB')
                
                return {
                    'processed_image': img,
                    'width': original_width,
                    'height': original_height,
                    'format': 'JPEG'
                }
                
        except Exception as e:
            logger.error(f'Error processing image: {str(e)}')
            raise Exception(f'Image processing failed: {str(e)}')
    
    def upload_file(self, file, event_id: Optional[str] = None, file_type: str = 'media', 
                   process_image: bool = True) -> Dict[str, Any]:
        """Upload file to storage backend with optional processing."""
        try:
            # Validate file
            validation = self.validate_file(file)
            if not validation['is_valid']:
                return {
                    'success': False,
                    'errors': validation['errors']
                }
            
            file_info = validation['file_info']
            
            # Generate file path
            file_path = self.generate_file_path(file.name, event_id, file_type)
            
            # Process image if needed
            if file_info['is_image'] and process_image:
                processed = self.process_image(file)
                
                # Save processed image to temporary file-like object
                from io import BytesIO
                output = BytesIO()
                processed['processed_image'].save(output, format='JPEG', quality=85, optimize=True)
                output.seek(0)
                
                # Create new file object
                from django.core.files.base import ContentFile
                processed_file = ContentFile(output.getvalue(), name=file.name)
                
                # Update file info
                file_info.update({
                    'width': processed['width'],
                    'height': processed['height'],
                    'size': len(output.getvalue())
                })
                
                upload_file = processed_file
            else:
                upload_file = file
            
            # Upload to storage backend
            upload_success = self.storage_backend.upload_file(upload_file, file_path)
            
            if upload_success:
                # Generate signed URL for immediate access
                signed_url = self.storage_backend.get_signed_url(file_path)
                
                return {
                    'success': True,
                    'file_path': file_path,
                    'file_info': file_info,
                    'signed_url': signed_url,
                    'storage_type': getattr(settings, 'STORAGE_TYPE', 'local')
                }
            else:
                return {
                    'success': False,
                    'errors': ['Failed to upload file to storage backend']
                }
                
        except Exception as e:
            logger.error(f'File upload error: {str(e)}')
            return {
                'success': False,
                'errors': [f'Upload failed: {str(e)}']
            }
    
    def delete_file(self, file_path: str) -> bool:
        """Delete file from storage backend."""
        try:
            return self.storage_backend.delete_file(file_path)
        except Exception as e:
            logger.error(f'File deletion error: {str(e)}')
            return False
    
    def get_signed_url(self, file_path: str, expiration: int = 3600) -> Optional[str]:
        """Get signed URL for file access."""
        try:
            return self.storage_backend.get_signed_url(file_path, expiration)
        except Exception as e:
            logger.error(f'Error generating signed URL: {str(e)}')
            return None
    
    def bulk_upload(self, files: List, event_id: Optional[str] = None, 
                   file_type: str = 'media') -> Dict[str, Any]:
        """Upload multiple files in batch."""
        results = {
            'successful_uploads': [],
            'failed_uploads': [],
            'total_files': len(files),
            'success_count': 0,
            'error_count': 0
        }
        
        for file in files:
            upload_result = self.upload_file(file, event_id, file_type)
            
            if upload_result['success']:
                results['successful_uploads'].append({
                    'file_name': file.name,
                    'file_path': upload_result['file_path'],
                    'file_info': upload_result['file_info'],
                    'signed_url': upload_result['signed_url']
                })
                results['success_count'] += 1
            else:
                results['failed_uploads'].append({
                    'file_name': file.name,
                    'errors': upload_result['errors']
                })
                results['error_count'] += 1
        
        return results


# Global media manager instance
media_manager = MediaManager()