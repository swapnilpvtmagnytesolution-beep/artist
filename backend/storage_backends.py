from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage
from storages.backends.gcloud import GoogleCloudStorage
import os
from urllib.parse import urljoin
from datetime import datetime, timedelta
import boto3
from botocore.exceptions import ClientError


class MediaStorage:
    """Base class for media storage backends."""
    
    def get_signed_url(self, file_path, expiration=3600):
        """Generate a signed URL for the given file path."""
        raise NotImplementedError("Subclasses must implement get_signed_url method")
    
    def upload_file(self, file, file_path):
        """Upload a file to the storage backend."""
        raise NotImplementedError("Subclasses must implement upload_file method")
    
    def delete_file(self, file_path):
        """Delete a file from the storage backend."""
        raise NotImplementedError("Subclasses must implement delete_file method")


class S3MediaStorage(S3Boto3Storage, MediaStorage):
    """Custom S3 storage backend for media files."""
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    region_name = settings.AWS_S3_REGION_NAME
    custom_domain = settings.AWS_S3_CUSTOM_DOMAIN
    file_overwrite = False
    default_acl = 'private'
    
    def get_signed_url(self, file_path, expiration=3600):
        """Generate a signed URL for S3 object."""
        try:
            s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=self.region_name
            )
            
            response = s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': file_path},
                ExpiresIn=expiration
            )
            return response
        except ClientError as e:
            print(f"Error generating signed URL: {e}")
            return None
    
    def upload_file(self, file, file_path):
        """Upload file to S3."""
        try:
            s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=self.region_name
            )
            
            s3_client.upload_fileobj(
                file,
                self.bucket_name,
                file_path,
                ExtraArgs={'ACL': 'private'}
            )
            return True
        except ClientError as e:
            print(f"Error uploading file: {e}")
            return False
    
    def delete_file(self, file_path):
        """Delete file from S3."""
        try:
            s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=self.region_name
            )
            
            s3_client.delete_object(Bucket=self.bucket_name, Key=file_path)
            return True
        except ClientError as e:
            print(f"Error deleting file: {e}")
            return False


class GCPMediaStorage(GoogleCloudStorage, MediaStorage):
    """Custom Google Cloud Storage backend for media files."""
    bucket_name = settings.GS_BUCKET_NAME
    file_overwrite = False
    default_acl = 'private'
    
    def get_signed_url(self, file_path, expiration=3600):
        """Generate a signed URL for GCS object."""
        try:
            from google.cloud import storage
            
            client = storage.Client()
            bucket = client.bucket(self.bucket_name)
            blob = bucket.blob(file_path)
            
            # Generate signed URL
            url = blob.generate_signed_url(
                version="v4",
                expiration=datetime.utcnow() + timedelta(seconds=expiration),
                method="GET"
            )
            return url
        except Exception as e:
            print(f"Error generating signed URL: {e}")
            return None
    
    def upload_file(self, file, file_path):
        """Upload file to GCS."""
        try:
            from google.cloud import storage
            
            client = storage.Client()
            bucket = client.bucket(self.bucket_name)
            blob = bucket.blob(file_path)
            
            blob.upload_from_file(file)
            return True
        except Exception as e:
            print(f"Error uploading file: {e}")
            return False
    
    def delete_file(self, file_path):
        """Delete file from GCS."""
        try:
            from google.cloud import storage
            
            client = storage.Client()
            bucket = client.bucket(self.bucket_name)
            blob = bucket.blob(file_path)
            
            blob.delete()
            return True
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False


class LocalMediaStorage(MediaStorage):
    """Local file system storage backend for development."""
    
    def get_signed_url(self, file_path, expiration=3600):
        """For local storage, return the media URL directly."""
        return urljoin(settings.MEDIA_URL, file_path)
    
    def upload_file(self, file, file_path):
        """Save file to local media directory."""
        try:
            full_path = os.path.join(settings.MEDIA_ROOT, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
            return True
        except Exception as e:
            print(f"Error uploading file: {e}")
            return False
    
    def delete_file(self, file_path):
        """Delete file from local media directory."""
        try:
            full_path = os.path.join(settings.MEDIA_ROOT, file_path)
            if os.path.exists(full_path):
                os.remove(full_path)
            return True
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False


def get_storage_backend():
    """Get the appropriate storage backend based on settings."""
    storage_type = getattr(settings, 'STORAGE_TYPE', 'local')
    
    if storage_type == 'aws':
        return S3MediaStorage()
    elif storage_type == 'gcp':
        return GCPMediaStorage()
    else:
        return LocalMediaStorage()


# Storage instances for different file types
media_storage = get_storage_backend()