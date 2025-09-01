from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json
import logging

from events.models import Event, Photo, Video
from media_manager import media_manager

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_media(request):
    """Upload single or multiple media files."""
    try:
        # Get event ID if provided
        event_id = request.data.get('event_id')
        event = None
        if event_id:
            event = get_object_or_404(Event, id=event_id)
        
        # Get file type (photo, video, reel)
        file_type = request.data.get('file_type', 'photo')
        
        # Get files from request
        files = request.FILES.getlist('files')
        if not files:
            return Response({
                'error': 'No files provided'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Process single file upload
        if len(files) == 1:
            file = files[0]
            upload_result = media_manager.upload_file(
                file=file,
                event_id=event_id,
                file_type=file_type
            )
            
            if upload_result['success']:
                # Create database record
                media_record = create_media_record(
                    file=file,
                    upload_result=upload_result,
                    event=event,
                    file_type=file_type,
                    user=request.user
                )
                
                return Response({
                    'success': True,
                    'media': {
                        'id': media_record.id,
                        'file_path': upload_result['file_path'],
                        'signed_url': upload_result['signed_url'],
                        'file_info': upload_result['file_info']
                    }
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'success': False,
                    'errors': upload_result['errors']
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Process bulk upload
        else:
            bulk_result = media_manager.bulk_upload(
                files=files,
                event_id=event_id,
                file_type=file_type
            )
            
            # Create database records for successful uploads
            created_records = []
            for upload_info in bulk_result['successful_uploads']:
                # Find the original file
                original_file = next(
                    (f for f in files if f.name == upload_info['file_name']), 
                    None
                )
                
                if original_file:
                    media_record = create_media_record(
                        file=original_file,
                        upload_result={
                            'file_path': upload_info['file_path'],
                            'file_info': upload_info['file_info'],
                            'signed_url': upload_info['signed_url']
                        },
                        event=event,
                        file_type=file_type,
                        user=request.user
                    )
                    created_records.append({
                        'id': media_record.id,
                        'file_name': upload_info['file_name'],
                        'file_path': upload_info['file_path'],
                        'signed_url': upload_info['signed_url']
                    })
            
            return Response({
                'success': True,
                'bulk_upload_result': {
                    'total_files': bulk_result['total_files'],
                    'success_count': bulk_result['success_count'],
                    'error_count': bulk_result['error_count'],
                    'successful_uploads': created_records,
                    'failed_uploads': bulk_result['failed_uploads']
                }
            }, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        logger.error(f'Media upload error: {str(e)}')
        return Response({
            'error': f'Upload failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def create_media_record(file, upload_result, event, file_type, user):
    """Create database record for uploaded media."""
    file_info = upload_result['file_info']
    
    common_data = {
        'title': file.name,
        'file_path': upload_result['file_path'],
        'size': file_info['size'],
        'event': event,
        'uploaded_by': user
    }
    
    if file_type == 'photo' or file_info.get('is_image'):
        return Photo.objects.create(
            image=upload_result['file_path'],
            width=file_info.get('width', 0),
            height=file_info.get('height', 0),
            **common_data
        )
    elif file_type in ['video', 'reel'] or file_info.get('is_video'):
        return Video.objects.create(
            video=upload_result['file_path'],
            duration=0,  # Will be updated by background task
            **common_data
        )
    else:
        # Default to photo
        return Photo.objects.create(
            image=upload_result['file_path'],
            **common_data
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_signed_url(request, media_type, media_id):
    """Get signed URL for media access."""
    try:
        # Get media object
        if media_type == 'photo':
            media_obj = get_object_or_404(Photo, id=media_id)
            file_path = media_obj.image.name if media_obj.image else media_obj.file_path
        elif media_type == 'video':
            media_obj = get_object_or_404(Video, id=media_id)
            file_path = media_obj.video.name if media_obj.video else media_obj.file_path
        else:
            return Response({
                'error': 'Invalid media type'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check permissions (basic check - can be enhanced)
        if not media_obj.event or not has_media_access(request.user, media_obj.event):
            return Response({
                'error': 'Access denied'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get expiration time (default 1 hour)
        expiration = int(request.GET.get('expiration', 3600))
        
        # Generate signed URL
        signed_url = media_manager.get_signed_url(file_path, expiration)
        
        if signed_url:
            return Response({
                'signed_url': signed_url,
                'expires_in': expiration
            })
        else:
            return Response({
                'error': 'Failed to generate signed URL'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    except Exception as e:
        logger.error(f'Error generating signed URL: {str(e)}')
        return Response({
            'error': f'Failed to get signed URL: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([permissions.IsAdminUser])
def delete_media(request, media_type, media_id):
    """Delete media file and database record."""
    try:
        # Get media object
        if media_type == 'photo':
            media_obj = get_object_or_404(Photo, id=media_id)
            file_path = media_obj.image.name if media_obj.image else media_obj.file_path
        elif media_type == 'video':
            media_obj = get_object_or_404(Video, id=media_id)
            file_path = media_obj.video.name if media_obj.video else media_obj.file_path
        else:
            return Response({
                'error': 'Invalid media type'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Delete file from storage
        deletion_success = media_manager.delete_file(file_path)
        
        # Delete database record
        media_obj.delete()
        
        return Response({
            'success': True,
            'file_deleted': deletion_success,
            'message': 'Media deleted successfully'
        })
    
    except Exception as e:
        logger.error(f'Error deleting media: {str(e)}')
        return Response({
            'error': f'Failed to delete media: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def media_info(request, media_type, media_id):
    """Get detailed information about a media file."""
    try:
        # Get media object
        if media_type == 'photo':
            media_obj = get_object_or_404(Photo, id=media_id)
            file_path = media_obj.image.name if media_obj.image else media_obj.file_path
        elif media_type == 'video':
            media_obj = get_object_or_404(Video, id=media_id)
            file_path = media_obj.video.name if media_obj.video else media_obj.file_path
        else:
            return Response({
                'error': 'Invalid media type'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check permissions
        if not media_obj.event or not has_media_access(request.user, media_obj.event):
            return Response({
                'error': 'Access denied'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Prepare response data
        media_data = {
            'id': media_obj.id,
            'title': media_obj.title,
            'description': getattr(media_obj, 'description', ''),
            'file_path': file_path,
            'size': media_obj.size,
            'created_at': media_obj.created_at,
            'event_id': media_obj.event.id if media_obj.event else None,
            'is_featured': getattr(media_obj, 'is_featured', False),
            'tags': getattr(media_obj, 'tags', [])
        }
        
        # Add type-specific data
        if media_type == 'photo':
            media_data.update({
                'width': getattr(media_obj, 'width', 0),
                'height': getattr(media_obj, 'height', 0),
                'type': 'photo'
            })
        elif media_type == 'video':
            media_data.update({
                'duration': getattr(media_obj, 'duration', 0),
                'type': 'video'
            })
        
        # Generate signed URL for access
        signed_url = media_manager.get_signed_url(file_path)
        if signed_url:
            media_data['signed_url'] = signed_url
        
        return Response(media_data)
    
    except Exception as e:
        logger.error(f'Error getting media info: {str(e)}')
        return Response({
            'error': f'Failed to get media info: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def storage_stats(request):
    """Get storage usage statistics."""
    try:
        from django.db.models import Sum, Count
        
        # Get storage statistics
        photo_stats = Photo.objects.aggregate(
            total_photos=Count('id'),
            total_photo_size=Sum('size')
        )
        
        video_stats = Video.objects.aggregate(
            total_videos=Count('id'),
            total_video_size=Sum('size')
        )
        
        total_size = (photo_stats['total_photo_size'] or 0) + (video_stats['total_video_size'] or 0)
        total_files = (photo_stats['total_photos'] or 0) + (video_stats['total_videos'] or 0)
        
        return Response({
            'storage_type': getattr(settings, 'STORAGE_TYPE', 'local'),
            'total_files': total_files,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2) if total_size else 0,
            'photos': {
                'count': photo_stats['total_photos'] or 0,
                'size_bytes': photo_stats['total_photo_size'] or 0,
                'size_mb': round((photo_stats['total_photo_size'] or 0) / (1024 * 1024), 2)
            },
            'videos': {
                'count': video_stats['total_videos'] or 0,
                'size_bytes': video_stats['total_video_size'] or 0,
                'size_mb': round((video_stats['total_video_size'] or 0) / (1024 * 1024), 2)
            }
        })
    
    except Exception as e:
        logger.error(f'Error getting storage stats: {str(e)}')
        return Response({
            'error': f'Failed to get storage stats: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def has_media_access(user, event):
    """Check if user has access to media for the given event."""
    # Admin users have access to all media
    if user.is_staff or user.is_superuser:
        return True
    
    # Event clients have access to their event's media
    if hasattr(user, 'event_client'):
        return user.event_client.event == event
    
    return False


@method_decorator(csrf_exempt, name='dispatch')
class MediaUploadView(View):
    """Class-based view for handling media uploads with progress tracking."""
    
    def post(self, request):
        """Handle file upload with progress tracking."""
        try:
            # Parse JSON data if content type is application/json
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST
            
            # This view can be extended to handle chunked uploads
            # and provide upload progress tracking
            
            return JsonResponse({
                'message': 'Use /api/media/upload/ endpoint for file uploads'
            })
        
        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=500)