from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework import status


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """API root endpoint with available endpoints."""
    return Response({
        'message': 'Welcome to Eddits API',
        'version': '1.0.0',
        'endpoints': {
            'admin': '/admin/',
            'auth': {
                'login': '/api/auth/login/',
                'refresh': '/api/auth/refresh/',
                'users': '/api/auth/users/',
                'event_login': '/api/auth/event-login/',
            },
            'events': {
                'events': '/api/events/',
                'photos': '/api/photos/',
                'videos': '/api/videos/',
                'reels': '/api/reels/',
            },
            'media': {
                'upload': '/api/media/upload/',
                'stats': '/api/media/stats/',
                'photo_url': '/api/media/photo/{id}/url/',
                'video_url': '/api/media/video/{id}/url/',
            },
            'email': {
                'queries': '/api/email/api/queries/',
                'appointments': '/api/email/api/appointments/',
                'templates': '/api/email/api/templates/',
                'logs': '/api/email/api/logs/',
                'stats': '/api/email/api/stats/',
            },
            'public': {
                'featured_events': '/api/events/featured/',
                'published_events': '/api/events/published/',
                'featured_photos': '/api/photos/featured/',
                'featured_videos': '/api/videos/featured/',
                'public_reels': '/api/reels/public/',
            }
        },
        'documentation': '/api/docs/',
    })


urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API Root
    path('api/', api_root, name='api-root'),
    
    # Authentication URLs
    path('api/auth/', include('users.urls')),
    
    # Events URLs
    path('api/', include('events.urls')),
    
    # Dashboard URLs
    path('api/dashboard/', include('dashboard.urls')),
    
    # Media URLs
    path('api/media/', include('media.urls')),
    
    # Email Service URLs
    path('api/email/', include('email_service.urls')),
    
    # Health check endpoint
    path('api/health/', include('core.views.health.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Admin site customization
admin.site.site_header = "Eddits Administration"
admin.site.site_title = "Eddits Admin Portal"
admin.site.index_title = "Welcome to Eddits Administration"