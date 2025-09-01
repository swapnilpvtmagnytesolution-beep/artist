from rest_framework import serializers
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

from .models import Event, Photo, Video, Reel
from users.serializers import EventClientSerializer


class PhotoSerializer(serializers.ModelSerializer):
    """Serializer for the Photo model."""
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Photo
        fields = ('id', 'event', 'title', 'description', 'image', 'image_url',
                  'width', 'height', 'size', 'tags', 'is_featured', 'created_at')
        read_only_fields = ('id', 'width', 'height', 'size', 'created_at')
    
    def get_image_url(self, obj):
        """Get the image URL with expiring signed URL if using cloud storage."""
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            url = obj.image.url
            if request is not None:
                return request.build_absolute_uri(url)
            return url
        return None


class VideoSerializer(serializers.ModelSerializer):
    """Serializer for the Video model."""
    video_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Video
        fields = ('id', 'event', 'title', 'description', 'video', 'video_url',
                  'thumbnail', 'thumbnail_url', 'duration', 'size', 'is_featured', 'created_at')
        read_only_fields = ('id', 'duration', 'size', 'created_at')
    
    def get_video_url(self, obj):
        """Get the video URL with expiring signed URL if using cloud storage."""
        request = self.context.get('request')
        if obj.video and hasattr(obj.video, 'url'):
            url = obj.video.url
            if request is not None:
                return request.build_absolute_uri(url)
            return url
        return None
    
    def get_thumbnail_url(self, obj):
        """Get the thumbnail URL with expiring signed URL if using cloud storage."""
        request = self.context.get('request')
        if obj.thumbnail and hasattr(obj.thumbnail, 'url'):
            url = obj.thumbnail.url
            if request is not None:
                return request.build_absolute_uri(url)
            return url
        return None


class ReelSerializer(serializers.ModelSerializer):
    """Serializer for the Reel model."""
    video_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Reel
        fields = ('id', 'event', 'title', 'description', 'video', 'video_url',
                  'thumbnail', 'thumbnail_url', 'duration', 'size', 'is_featured', 'created_at')
        read_only_fields = ('id', 'duration', 'size', 'created_at')
    
    def get_video_url(self, obj):
        """Get the video URL with expiring signed URL if using cloud storage."""
        request = self.context.get('request')
        if obj.video and hasattr(obj.video, 'url'):
            url = obj.video.url
            if request is not None:
                return request.build_absolute_uri(url)
            return url
        return None
    
    def get_thumbnail_url(self, obj):
        """Get the thumbnail URL with expiring signed URL if using cloud storage."""
        request = self.context.get('request')
        if obj.thumbnail and hasattr(obj.thumbnail, 'url'):
            url = obj.thumbnail.url
            if request is not None:
                return request.build_absolute_uri(url)
            return url
        return None


class EventSerializer(serializers.ModelSerializer):
    """Serializer for the Event model."""
    cover_photo_url = serializers.SerializerMethodField()
    clients = EventClientSerializer(many=True, read_only=True)
    days_until_expiry = serializers.SerializerMethodField()
    
    class Meta:
        model = Event
        fields = ('id', 'title', 'description', 'event_date', 'event_id',
                  'is_password_protected', 'password', 'cover_photo', 'cover_photo_url',
                  'expiry_date', 'allow_downloads', 'is_featured', 'is_published',
                  'clients', 'photo_count', 'video_count', 'reel_count',
                  'days_until_expiry', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def get_cover_photo_url(self, obj):
        """Get the cover photo URL with expiring signed URL if using cloud storage."""
        request = self.context.get('request')
        if obj.cover_photo and hasattr(obj.cover_photo, 'url'):
            url = obj.cover_photo.url
            if request is not None:
                return request.build_absolute_uri(url)
            return url
        return None
    
    def get_days_until_expiry(self, obj):
        """Get the number of days until the event expires."""
        if obj.expiry_date:
            delta = obj.expiry_date - timezone.now().date()
            return max(0, delta.days)
        
        # If no expiry date is set, use the default expiry period from settings
        default_expiry_days = settings.EDDITS_PORTAL.get('DEFAULT_ALBUM_EXPIRY_DAYS', 90)
        default_expiry = obj.event_date + timedelta(days=default_expiry_days)
        delta = default_expiry - timezone.now().date()
        return max(0, delta.days)


class EventDetailSerializer(EventSerializer):
    """Detailed serializer for the Event model including photos, videos, and reels."""
    photos = PhotoSerializer(many=True, read_only=True)
    videos = VideoSerializer(many=True, read_only=True)
    reels = ReelSerializer(many=True, read_only=True)
    
    class Meta(EventSerializer.Meta):
        fields = EventSerializer.Meta.fields + ('photos', 'videos', 'reels')