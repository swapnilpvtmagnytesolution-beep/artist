from django.urls import path
from . import views

app_name = 'media'

urlpatterns = [
    # Media upload endpoints
    path('upload/', views.upload_media, name='upload_media'),
    path('upload/chunked/', views.MediaUploadView.as_view(), name='chunked_upload'),
    
    # Media access endpoints
    path('<str:media_type>/<int:media_id>/url/', views.get_signed_url, name='get_signed_url'),
    path('<str:media_type>/<int:media_id>/info/', views.media_info, name='media_info'),
    
    # Media management endpoints
    path('<str:media_type>/<int:media_id>/delete/', views.delete_media, name='delete_media'),
    
    # Storage statistics
    path('stats/', views.storage_stats, name='storage_stats'),
]