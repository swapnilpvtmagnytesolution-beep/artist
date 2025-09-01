from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage
from storages.backends.gcloud import GoogleCloudStorage

class MediaStorage:
    """Custom storage backend for media files.
    
    This class provides a unified interface for storing media files
    regardless of the underlying storage provider (S3, GCS, DO Spaces, etc.).
    """
    
    def __new__(cls, *args, **kwargs):
        storage_type = settings.STORAGE_TYPE
        
        if storage_type == 's3' or storage_type == 'do':
            return S3MediaStorage()
        elif storage_type == 'gcs':
            return GCSMediaStorage()
        else:
            # Default to local file storage
            from django.core.files.storage import FileSystemStorage
            return FileSystemStorage()


class S3MediaStorage(S3Boto3Storage):
    """Storage backend for AWS S3 or DigitalOcean Spaces."""
    location = 'media'
    file_overwrite = False
    default_acl = 'private'
    custom_domain = False  # Use signed URLs instead of custom domain


class GCSMediaStorage(GoogleCloudStorage):
    """Storage backend for Google Cloud Storage."""
    location = 'media'
    file_overwrite = False
    default_acl = 'private'
    custom_domain = False  # Use signed URLs instead of custom domain