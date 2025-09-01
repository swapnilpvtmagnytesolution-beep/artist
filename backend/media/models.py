from django.db import models
from django.contrib.auth import get_user_model
from events.models import Event
import uuid

User = get_user_model()

class MediaFile(models.Model):
    """Model to track uploaded media files"""
    
    MEDIA_TYPES = [
        ('photo', 'Photo'),
        ('video', 'Video'),
        ('reel', 'Reel'),
        ('document', 'Document'),
    ]
    
    STORAGE_PROVIDERS = [
        ('local', 'Local Storage'),
        ('aws', 'AWS S3'),
        ('gcp', 'Google Cloud Storage'),
        ('digitalocean', 'DigitalOcean Spaces'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='media_files')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_media')
    
    # File information
    file_name = models.CharField(max_length=255)
    original_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500)  # Path in storage
    file_size = models.BigIntegerField()  # Size in bytes
    file_type = models.CharField(max_length=20, choices=MEDIA_TYPES)
    mime_type = models.CharField(max_length=100)
    
    # Storage information
    storage_provider = models.CharField(max_length=20, choices=STORAGE_PROVIDERS, default='local')
    storage_bucket = models.CharField(max_length=100, blank=True, null=True)
    
    # Metadata
    width = models.IntegerField(blank=True, null=True)  # For images/videos
    height = models.IntegerField(blank=True, null=True)  # For images/videos
    duration = models.FloatField(blank=True, null=True)  # For videos in seconds
    
    # Processing status
    is_processed = models.BooleanField(default=False)
    processing_error = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'media_files'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['event', 'file_type']),
            models.Index(fields=['uploaded_by']),
            models.Index(fields=['created_at']),
            models.Index(fields=['storage_provider']),
        ]
    
    def __str__(self):
        return f"{self.original_name} ({self.file_type})"
    
    @property
    def file_size_mb(self):
        """Return file size in MB"""
        return round(self.file_size / (1024 * 1024), 2)
    
    @property
    def is_image(self):
        """Check if file is an image"""
        return self.file_type == 'photo'
    
    @property
    def is_video(self):
        """Check if file is a video"""
        return self.file_type in ['video', 'reel']


class MediaProcessingJob(models.Model):
    """Model to track media processing jobs"""
    
    JOB_TYPES = [
        ('resize', 'Image Resize'),
        ('watermark', 'Add Watermark'),
        ('thumbnail', 'Generate Thumbnail'),
        ('compress', 'Video Compression'),
        ('transcode', 'Video Transcoding'),
    ]
    
    JOB_STATUS = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    media_file = models.ForeignKey(MediaFile, on_delete=models.CASCADE, related_name='processing_jobs')
    job_type = models.CharField(max_length=20, choices=JOB_TYPES)
    status = models.CharField(max_length=20, choices=JOB_STATUS, default='pending')
    
    # Job parameters (JSON)
    parameters = models.JSONField(default=dict, blank=True)
    
    # Results
    result_file_path = models.CharField(max_length=500, blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'media_processing_jobs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['media_file', 'job_type']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.job_type} for {self.media_file.original_name}"


class StorageUsage(models.Model):
    """Model to track storage usage statistics"""
    
    event = models.OneToOneField(Event, on_delete=models.CASCADE, related_name='storage_usage')
    
    # Storage statistics
    total_files = models.IntegerField(default=0)
    total_size_bytes = models.BigIntegerField(default=0)
    
    # File type breakdown
    photo_count = models.IntegerField(default=0)
    photo_size_bytes = models.BigIntegerField(default=0)
    video_count = models.IntegerField(default=0)
    video_size_bytes = models.BigIntegerField(default=0)
    reel_count = models.IntegerField(default=0)
    reel_size_bytes = models.BigIntegerField(default=0)
    
    # Timestamps
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'storage_usage'
    
    def __str__(self):
        return f"Storage usage for {self.event.name}"
    
    @property
    def total_size_mb(self):
        """Return total size in MB"""
        return round(self.total_size_bytes / (1024 * 1024), 2)
    
    @property
    def total_size_gb(self):
        """Return total size in GB"""
        return round(self.total_size_bytes / (1024 * 1024 * 1024), 2)
    
    def update_stats(self):
        """Update storage statistics from related media files"""
        from django.db.models import Count, Sum
        
        # Get aggregated data
        stats = self.event.media_files.aggregate(
            total_files=Count('id'),
            total_size=Sum('file_size'),
            photo_count=Count('id', filter=models.Q(file_type='photo')),
            photo_size=Sum('file_size', filter=models.Q(file_type='photo')),
            video_count=Count('id', filter=models.Q(file_type='video')),
            video_size=Sum('file_size', filter=models.Q(file_type='video')),
            reel_count=Count('id', filter=models.Q(file_type='reel')),
            reel_size=Sum('file_size', filter=models.Q(file_type='reel')),
        )
        
        # Update fields
        self.total_files = stats['total_files'] or 0
        self.total_size_bytes = stats['total_size'] or 0
        self.photo_count = stats['photo_count'] or 0
        self.photo_size_bytes = stats['photo_size'] or 0
        self.video_count = stats['video_count'] or 0
        self.video_size_bytes = stats['video_size'] or 0
        self.reel_count = stats['reel_count'] or 0
        self.reel_size_bytes = stats['reel_size'] or 0
        
        self.save()