from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Event, Photo, Video, Reel


class PhotoInline(admin.TabularInline):
    """Inline admin for photos."""
    model = Photo
    extra = 0
    fields = ('image', 'title', 'is_featured')
    readonly_fields = ('created_at',)


class VideoInline(admin.TabularInline):
    """Inline admin for videos."""
    model = Video
    extra = 0
    fields = ('video', 'thumbnail', 'title', 'is_featured')
    readonly_fields = ('created_at',)


class ReelInline(admin.TabularInline):
    """Inline admin for reels."""
    model = Reel
    extra = 0
    fields = ('video', 'thumbnail', 'title', 'is_featured')
    readonly_fields = ('created_at',)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """Admin configuration for the Event model."""
    list_display = ('title', 'event_date', 'event_id', 'is_password_protected', 
                    'is_published', 'is_featured', 'photo_count', 'video_count', 'reel_count')
    list_filter = ('event_date', 'is_published', 'is_featured', 'is_password_protected')
    search_fields = ('title', 'description', 'event_id')
    readonly_fields = ('created_at', 'updated_at', 'photo_count', 'video_count', 'reel_count')
    date_hierarchy = 'event_date'
    
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'event_date', 'cover_photo')
        }),
        (_('Access Settings'), {
            'fields': ('event_id', 'is_password_protected', 'password', 'expiry_date', 'allow_downloads')
        }),
        (_('Status'), {
            'fields': ('is_published', 'is_featured')
        }),
        (_('Clients'), {
            'fields': ('clients',)
        }),
        (_('Statistics'), {
            'fields': ('photo_count', 'video_count', 'reel_count', 'created_at', 'updated_at')
        }),
    )
    
    inlines = [PhotoInline, VideoInline, ReelInline]
    
    def get_queryset(self, request):
        """Prefetch related objects to improve admin performance."""
        return super().get_queryset(request).prefetch_related('photos', 'videos', 'reels', 'clients')


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    """Admin configuration for the Photo model."""
    list_display = ('title', 'event', 'created_at', 'is_featured')
    list_filter = ('created_at', 'is_featured', 'event')
    search_fields = ('title', 'description', 'event__title')
    readonly_fields = ('width', 'height', 'size', 'created_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('event', 'title', 'description', 'image', 'is_featured')
        }),
        (_('Metadata'), {
            'fields': ('width', 'height', 'size', 'tags', 'created_at', 'updated_at')
        }),
    )


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    """Admin configuration for the Video model."""
    list_display = ('title', 'event', 'created_at', 'is_featured')
    list_filter = ('created_at', 'is_featured', 'event')
    search_fields = ('title', 'description', 'event__title')
    readonly_fields = ('duration', 'size', 'created_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('event', 'title', 'description', 'video', 'thumbnail', 'is_featured')
        }),
        (_('Metadata'), {
            'fields': ('duration', 'size', 'created_at', 'updated_at')
        }),
    )


@admin.register(Reel)
class ReelAdmin(admin.ModelAdmin):
    """Admin configuration for the Reel model."""
    list_display = ('title', 'event', 'created_at', 'is_featured')
    list_filter = ('created_at', 'is_featured', 'event')
    search_fields = ('title', 'description', 'event__title')
    readonly_fields = ('duration', 'size', 'created_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('event', 'title', 'description', 'video', 'thumbnail', 'is_featured')
        }),
        (_('Metadata'), {
            'fields': ('duration', 'size', 'created_at', 'updated_at')
        }),
    )