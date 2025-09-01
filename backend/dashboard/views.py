from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model

from events.models import Event, Photo, Video, Reel
from users.models import EventClient

User = get_user_model()


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def dashboard_stats(request):
    """Get comprehensive dashboard statistics."""
    
    # Date ranges for analytics
    today = timezone.now().date()
    last_30_days = today - timedelta(days=30)
    last_7_days = today - timedelta(days=7)
    
    # Event statistics
    total_events = Event.objects.count()
    published_events = Event.objects.filter(is_published=True).count()
    featured_events = Event.objects.filter(is_featured=True).count()
    recent_events = Event.objects.filter(created_at__date__gte=last_30_days).count()
    
    # Media statistics
    total_photos = Photo.objects.count()
    total_videos = Video.objects.count()
    total_reels = Reel.objects.count()
    
    # Recent media uploads
    recent_photos = Photo.objects.filter(created_at__date__gte=last_7_days).count()
    recent_videos = Video.objects.filter(created_at__date__gte=last_7_days).count()
    recent_reels = Reel.objects.filter(created_at__date__gte=last_7_days).count()
    
    # User statistics
    total_users = User.objects.count()
    total_clients = EventClient.objects.count()
    recent_users = User.objects.filter(date_joined__date__gte=last_30_days).count()
    
    # Storage statistics (approximate)
    total_media_files = total_photos + total_videos + total_reels
    
    # Event engagement statistics
    events_with_clients = Event.objects.annotate(
        client_count=Count('clients')
    ).filter(client_count__gt=0).count()
    
    # Popular events (by client count)
    popular_events = Event.objects.annotate(
        client_count=Count('clients')
    ).filter(is_published=True).order_by('-client_count')[:5]
    
    popular_events_data = []
    for event in popular_events:
        popular_events_data.append({
            'id': event.id,
            'title': event.title,
            'event_id': event.event_id,
            'client_count': event.client_count,
            'photo_count': event.photos.count(),
            'video_count': event.videos.count(),
            'reel_count': event.reels.count(),
        })
    
    # Recent activity
    recent_events_data = Event.objects.filter(
        created_at__date__gte=last_7_days
    ).order_by('-created_at')[:10]
    
    recent_activity = []
    for event in recent_events_data:
        recent_activity.append({
            'id': event.id,
            'title': event.title,
            'event_id': event.event_id,
            'created_at': event.created_at,
            'is_published': event.is_published,
            'is_featured': event.is_featured,
        })
    
    # Monthly statistics for charts
    monthly_stats = []
    for i in range(12):
        month_start = today.replace(day=1) - timedelta(days=30 * i)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        month_events = Event.objects.filter(
            created_at__date__gte=month_start,
            created_at__date__lte=month_end
        ).count()
        
        month_photos = Photo.objects.filter(
            created_at__date__gte=month_start,
            created_at__date__lte=month_end
        ).count()
        
        monthly_stats.append({
            'month': month_start.strftime('%Y-%m'),
            'events': month_events,
            'photos': month_photos,
        })
    
    monthly_stats.reverse()  # Show oldest to newest
    
    return Response({
        'overview': {
            'total_events': total_events,
            'published_events': published_events,
            'featured_events': featured_events,
            'recent_events': recent_events,
            'total_photos': total_photos,
            'total_videos': total_videos,
            'total_reels': total_reels,
            'total_media_files': total_media_files,
            'total_users': total_users,
            'total_clients': total_clients,
            'recent_users': recent_users,
            'events_with_clients': events_with_clients,
        },
        'recent_uploads': {
            'photos': recent_photos,
            'videos': recent_videos,
            'reels': recent_reels,
        },
        'popular_events': popular_events_data,
        'recent_activity': recent_activity,
        'monthly_stats': monthly_stats,
        'generated_at': timezone.now(),
    })


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def event_analytics(request, event_id=None):
    """Get detailed analytics for a specific event or all events."""
    
    if event_id:
        try:
            event = Event.objects.get(id=event_id)
            
            # Event-specific analytics
            photo_count = event.photos.count()
            video_count = event.videos.count()
            reel_count = event.reels.count()
            client_count = event.clients.count()
            
            # Featured media counts
            featured_photos = event.photos.filter(is_featured=True).count()
            featured_videos = event.videos.filter(is_featured=True).count()
            featured_reels = event.reels.filter(is_featured=True).count()
            
            return Response({
                'event': {
                    'id': event.id,
                    'title': event.title,
                    'event_id': event.event_id,
                    'description': event.description,
                    'event_date': event.event_date,
                    'created_at': event.created_at,
                    'is_published': event.is_published,
                    'is_featured': event.is_featured,
                    'is_password_protected': event.is_password_protected,
                    'expires_at': event.expires_at,
                    'allow_downloads': event.allow_downloads,
                },
                'analytics': {
                    'photo_count': photo_count,
                    'video_count': video_count,
                    'reel_count': reel_count,
                    'client_count': client_count,
                    'featured_photos': featured_photos,
                    'featured_videos': featured_videos,
                    'featured_reels': featured_reels,
                    'total_media': photo_count + video_count + reel_count,
                },
                'clients': list(event.clients.values(
                    'id', 'name', 'email', 'phone', 'created_at'
                )),
            })
            
        except Event.DoesNotExist:
            return Response(
                {'error': 'Event not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    else:
        # All events analytics
        events = Event.objects.annotate(
            photo_count=Count('photos'),
            video_count=Count('videos'),
            reel_count=Count('reels'),
            client_count=Count('clients')
        ).order_by('-created_at')
        
        events_data = []
        for event in events:
            events_data.append({
                'id': event.id,
                'title': event.title,
                'event_id': event.event_id,
                'event_date': event.event_date,
                'created_at': event.created_at,
                'is_published': event.is_published,
                'is_featured': event.is_featured,
                'photo_count': event.photo_count,
                'video_count': event.video_count,
                'reel_count': event.reel_count,
                'client_count': event.client_count,
                'total_media': event.photo_count + event.video_count + event.reel_count,
            })
        
        return Response({
            'events': events_data,
            'total_events': len(events_data),
        })


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def media_analytics(request):
    """Get media upload and storage analytics."""
    
    # Date ranges
    today = timezone.now().date()
    last_30_days = today - timedelta(days=30)
    last_7_days = today - timedelta(days=7)
    
    # Media type distribution
    media_distribution = {
        'photos': Photo.objects.count(),
        'videos': Video.objects.count(),
        'reels': Reel.objects.count(),
    }
    
    # Recent uploads by type
    recent_uploads = {
        'photos': Photo.objects.filter(created_at__date__gte=last_7_days).count(),
        'videos': Video.objects.filter(created_at__date__gte=last_7_days).count(),
        'reels': Reel.objects.filter(created_at__date__gte=last_7_days).count(),
    }
    
    # Featured media
    featured_media = {
        'photos': Photo.objects.filter(is_featured=True).count(),
        'videos': Video.objects.filter(is_featured=True).count(),
        'reels': Reel.objects.filter(is_featured=True).count(),
    }
    
    # Daily upload trends (last 30 days)
    daily_uploads = []
    for i in range(30):
        date = today - timedelta(days=i)
        
        daily_photos = Photo.objects.filter(created_at__date=date).count()
        daily_videos = Video.objects.filter(created_at__date=date).count()
        daily_reels = Reel.objects.filter(created_at__date=date).count()
        
        daily_uploads.append({
            'date': date.strftime('%Y-%m-%d'),
            'photos': daily_photos,
            'videos': daily_videos,
            'reels': daily_reels,
            'total': daily_photos + daily_videos + daily_reels,
        })
    
    daily_uploads.reverse()  # Show oldest to newest
    
    # Top events by media count
    top_events = Event.objects.annotate(
        total_media=Count('photos') + Count('videos') + Count('reels')
    ).filter(total_media__gt=0).order_by('-total_media')[:10]
    
    top_events_data = []
    for event in top_events:
        top_events_data.append({
            'id': event.id,
            'title': event.title,
            'event_id': event.event_id,
            'photo_count': event.photos.count(),
            'video_count': event.videos.count(),
            'reel_count': event.reels.count(),
            'total_media': event.photos.count() + event.videos.count() + event.reels.count(),
        })
    
    return Response({
        'media_distribution': media_distribution,
        'recent_uploads': recent_uploads,
        'featured_media': featured_media,
        'daily_uploads': daily_uploads,
        'top_events': top_events_data,
        'generated_at': timezone.now(),
    })


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def user_analytics(request):
    """Get user and client analytics."""
    
    # Date ranges
    today = timezone.now().date()
    last_30_days = today - timedelta(days=30)
    last_7_days = today - timedelta(days=7)
    
    # User statistics
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    staff_users = User.objects.filter(is_staff=True).count()
    superusers = User.objects.filter(is_superuser=True).count()
    
    # Recent registrations
    recent_users = User.objects.filter(date_joined__date__gte=last_30_days).count()
    weekly_users = User.objects.filter(date_joined__date__gte=last_7_days).count()
    
    # Client statistics
    total_clients = EventClient.objects.count()
    recent_clients = EventClient.objects.filter(created_at__date__gte=last_30_days).count()
    
    # User registration trends (last 30 days)
    registration_trends = []
    for i in range(30):
        date = today - timedelta(days=i)
        daily_registrations = User.objects.filter(date_joined__date=date).count()
        daily_clients = EventClient.objects.filter(created_at__date=date).count()
        
        registration_trends.append({
            'date': date.strftime('%Y-%m-%d'),
            'users': daily_registrations,
            'clients': daily_clients,
        })
    
    registration_trends.reverse()  # Show oldest to newest
    
    # Recent users
    recent_users_data = User.objects.filter(
        date_joined__date__gte=last_7_days
    ).order_by('-date_joined')[:10]
    
    recent_users_list = []
    for user in recent_users_data:
        recent_users_list.append({
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'date_joined': user.date_joined,
            'is_active': user.is_active,
            'is_staff': user.is_staff,
        })
    
    return Response({
        'user_stats': {
            'total_users': total_users,
            'active_users': active_users,
            'staff_users': staff_users,
            'superusers': superusers,
            'recent_users': recent_users,
            'weekly_users': weekly_users,
        },
        'client_stats': {
            'total_clients': total_clients,
            'recent_clients': recent_clients,
        },
        'registration_trends': registration_trends,
        'recent_users': recent_users_list,
        'generated_at': timezone.now(),
    })