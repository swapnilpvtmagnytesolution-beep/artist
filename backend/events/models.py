import os
import uuid
from datetime import timedelta

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from users.models import EventClient


def event_cover_upload_path(instance, filename):
    """Generate a unique path for event cover photos."""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('events', str(instance.id), 'cover', filename)


def photo_upload_path(instance, filename):
    """Generate a unique path for event photos."""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('events', str(instance.event.id), 'photos', filename)


def video_upload_path(instance, filename):
    """Generate a unique path for event videos."""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('events', str(instance.event.id), 'videos', filename)


def reel_upload_path(instance, filename):
    """Generate a unique path for event reels."""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('events', str(instance.event.id), 'reels', filename)


class Event(models.Model):
    """Model for photography events."""
    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    event_date = models.DateField(_('event date'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Event access credentials
    event_id = models.CharField(_('event ID'), max_length=20, unique=True)
    is_password_protected = models.BooleanField(_('password protected'), default=True)
    password = models.CharField(_('password'), max_length=50, blank=True, null=True)
    
    # Event cover
    cover_photo = models.ImageField(_('cover photo'), upload_to=event_cover_upload_path, blank=True, null=True)
    
    # Event expiry
    expiry_date = models.DateField(_('expiry date'), blank=True, null=True)
    
    # Event settings
    allow_downloads = models.BooleanField(_('allow downloads'), default=True)
    is_featured = models.BooleanField(_('featured'), default=False)
    is_published = models.BooleanField(_('published'), default=False)
    
    # Event clients
    clients = models.ManyToManyField(EventClient, related_name='events', blank=True)
    
    class Meta:
        ordering = ['-event_date']
        verbose_name = _('event')
        verbose_name_plural = _('events')
    
    def __str__(self):
        return self.title
    
    @property
    def is_expired(self):
        """Check if the event has expired."""
        if not self.expiry_date:
            # If no expiry date is set, use the default expiry period from settings
            default_expiry_days = settings.EDDITS_PORTAL.get('DEFAULT_ALBUM_EXPIRY_DAYS', 90)
            default_expiry = self.event_date + timedelta(days=default_expiry_days)
            return timezone.now().date() > default_expiry
        return timezone.now().date() > self.expiry_date
    
    @property
    def photo_count(self):
        """Get the number of photos in this event."""
        return self.photos.count()
    
    @property
    def video_count(self):
        """Get the number of videos in this event."""
        return self.videos.count()
    
    @property
    def reel_count(self):
        """Get the number of reels in this event."""
        return self.reels.count()


class Photo(models.Model):
    """Model for event photos."""
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='photos')
    title = models.CharField(_('title'), max_length=255, blank=True)
    description = models.TextField(_('description'), blank=True)
    image = models.ImageField(_('image'), upload_to=photo_upload_path)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Photo metadata
    width = models.PositiveIntegerField(_('width'), blank=True, null=True)
    height = models.PositiveIntegerField(_('height'), blank=True, null=True)
    size = models.PositiveIntegerField(_('size in bytes'), blank=True, null=True)
    
    # AI tagging
    tags = models.JSONField(_('tags'), blank=True, null=True)
    
    # Featured status
    is_featured = models.BooleanField(_('featured'), default=False)
    
    class Meta:
        ordering = ['created_at']
        verbose_name = _('photo')
        verbose_name_plural = _('photos')
    
    def __str__(self):
        return f"{self.event.title} - {self.title or 'Photo'}"
    
    def save(self, *args, **kwargs):
        """Save photo with metadata."""
        if not self.pk and self.image:  # Only on creation
            # Get image dimensions and size
            self.width = self.image.width
            self.height = self.image.height
            self.size = self.image.size
            
            # Set title from filename if not provided
            if not self.title:
                self.title = os.path.splitext(os.path.basename(self.image.name))[0]
        
        super().save(*args, **kwargs)


class Video(models.Model):
    """Model for event videos."""
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='videos')
    title = models.CharField(_('title'), max_length=255, blank=True)
    description = models.TextField(_('description'), blank=True)
    video = models.FileField(_('video'), upload_to=video_upload_path)
    thumbnail = models.ImageField(_('thumbnail'), upload_to=video_upload_path, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Video metadata
    duration = models.PositiveIntegerField(_('duration in seconds'), blank=True, null=True)
    size = models.PositiveIntegerField(_('size in bytes'), blank=True, null=True)
    
    # Featured status
    is_featured = models.BooleanField(_('featured'), default=False)
    
    class Meta:
        ordering = ['created_at']
        verbose_name = _('video')
        verbose_name_plural = _('videos')
    
    def __str__(self):
        return f"{self.event.title} - {self.title or 'Video'}"
    
    def save(self, *args, **kwargs):
        """Save video with metadata."""
        if not self.pk and self.video:  # Only on creation
            # Get video size
            self.size = self.video.size
            
            # Set title from filename if not provided
            if not self.title:
                self.title = os.path.splitext(os.path.basename(self.video.name))[0]
        
        super().save(*args, **kwargs)


class Reel(models.Model):
    """Model for event reels (short highlight videos)."""
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='reels')
    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    video = models.FileField(_('video'), upload_to=reel_upload_path)
    thumbnail = models.ImageField(_('thumbnail'), upload_to=reel_upload_path, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Reel metadata
    duration = models.PositiveIntegerField(_('duration in seconds'), blank=True, null=True)
    size = models.PositiveIntegerField(_('size in bytes'), blank=True, null=True)
    
    # Featured status
    is_featured = models.BooleanField(_('featured'), default=False)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('reel')
        verbose_name_plural = _('reels')
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        """Save reel with metadata."""
        if not self.pk and self.video:  # Only on creation
            # Get video size
            self.size = self.video.size
        
        super().save(*args, **kwargs)