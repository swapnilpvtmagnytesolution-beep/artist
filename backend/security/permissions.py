from rest_framework import permissions
from django.contrib.auth.models import AnonymousUser
from events.models import Event, EventClient
from django.shortcuts import get_object_or_404


class IsOwnerOrAdmin(permissions.BasePermission):
    """Permission to only allow owners of an object or admin users to edit it."""
    
    def has_object_permission(self, request, view, obj):
        # Read permissions for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        
        # Write permissions only to the owner or admin
        if hasattr(obj, 'user'):
            return obj.user == request.user or request.user.is_staff
        elif hasattr(obj, 'created_by'):
            return obj.created_by == request.user or request.user.is_staff
        
        # Default to admin only
        return request.user.is_staff


class IsAdminOrReadOnly(permissions.BasePermission):
    """Permission to only allow admin users to edit, but allow read access to authenticated users."""
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_staff


class EventAccessPermission(permissions.BasePermission):
    """Custom permission to check event access based on password or client relationship."""
    
    def has_permission(self, request, view):
        # Admin users have full access
        if request.user.is_staff:
            return True
        
        # For event-specific views, check access
        if hasattr(view, 'get_event'):
            event = view.get_event()
            if event:
                return self.check_event_access(request, event)
        
        # For list views, allow access (filtering will be done in queryset)
        return True
    
    def has_object_permission(self, request, view, obj):
        # Admin users have full access
        if request.user.is_staff:
            return True
        
        # Get the related event
        event = None
        if hasattr(obj, 'event'):
            event = obj.event
        elif isinstance(obj, Event):
            event = obj
        
        if event:
            return self.check_event_access(request, event)
        
        return False
    
    def check_event_access(self, request, event):
        """Check if user has access to the event."""
        
        # Check if event is published
        if not event.is_published:
            return False
        
        # Check if event has expired
        if event.is_expired:
            return False
        
        # Check session for event access
        session_key = f"event_access:{event.event_id}"
        if request.session.get(session_key, False):
            return True
        
        # Check if user is an event client
        if request.user.is_authenticated:
            try:
                EventClient.objects.get(
                    email=request.user.email,
                    events=event
                )
                # Grant session access
                request.session[session_key] = True
                return True
            except EventClient.DoesNotExist:
                pass
        
        # For password-protected events, check if password was provided
        if event.is_password_protected:
            # This will be handled by the verify_access endpoint
            return False
        
        # Public events are accessible
        return True


class MediaDownloadPermission(permissions.BasePermission):
    """Permission for media downloads with additional restrictions."""
    
    def has_permission(self, request, view):
        # Admin users have full access
        if request.user.is_staff:
            return True
        
        # Check if downloads are allowed for the event
        if hasattr(view, 'get_object'):
            obj = view.get_object()
            if hasattr(obj, 'event'):
                event = obj.event
                
                # Check if downloads are allowed
                if not event.allow_downloads:
                    return False
                
                # Check event access
                return EventAccessPermission().check_event_access(request, event)
        
        return False


class DashboardPermission(permissions.BasePermission):
    """Permission for dashboard and analytics access."""
    
    def has_permission(self, request, view):
        # Only admin users can access dashboard
        return request.user.is_authenticated and request.user.is_staff


class EventClientPermission(permissions.BasePermission):
    """Permission for event client management."""
    
    def has_permission(self, request, view):
        # Admin users have full access
        if request.user.is_staff:
            return True
        
        # Authenticated users can view their own client records
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        
        # Only admin can create/update/delete
        return False
    
    def has_object_permission(self, request, view, obj):
        # Admin users have full access
        if request.user.is_staff:
            return True
        
        # Users can only view their own client records
        if request.method in permissions.SAFE_METHODS:
            return obj.email == request.user.email
        
        return False


class PublicEventPermission(permissions.BasePermission):
    """Permission for public event access (no authentication required)."""
    
    def has_permission(self, request, view):
        # Allow all users to access public events
        return True
    
    def has_object_permission(self, request, view, obj):
        # Only allow access to published events
        if hasattr(obj, 'is_published'):
            return obj.is_published
        elif hasattr(obj, 'event'):
            return obj.event.is_published
        
        return True


class WatermarkPermission(permissions.BasePermission):
    """Permission to control watermark application on media."""
    
    def has_permission(self, request, view):
        # Check if user has paid access or is admin
        if request.user.is_staff:
            return True
        
        # Check if user has premium access (this could be extended)
        # For now, all authenticated users get watermarked content
        return request.user.is_authenticated
    
    def should_apply_watermark(self, request, obj):
        """Determine if watermark should be applied to media."""
        
        # Admin users get unwatermarked content
        if request.user.is_staff:
            return False
        
        # Check if user has premium access for this event
        if hasattr(obj, 'event'):
            event = obj.event
            
            # Check if user is a premium client (this could be extended)
            try:
                client = EventClient.objects.get(
                    email=request.user.email,
                    events=event
                )
                # For now, all clients get watermarked content
                # This could be extended to check for premium status
                return True
            except EventClient.DoesNotExist:
                pass
        
        # Default to watermarked content
        return True


class RateLimitPermission(permissions.BasePermission):
    """Permission to implement API rate limiting."""
    
    def has_permission(self, request, view):
        # Admin users are exempt from rate limiting
        if request.user.is_staff:
            return True
        
        # Rate limiting is handled by middleware
        # This permission is just for documentation
        return True


class IPWhitelistPermission(permissions.BasePermission):
    """Permission to restrict access based on IP whitelist."""
    
    def has_permission(self, request, view):
        # This is handled by middleware
        # This permission is just for documentation
        return True


class MaintenanceModePermission(permissions.BasePermission):
    """Permission to handle maintenance mode."""
    
    def has_permission(self, request, view):
        from django.conf import settings
        
        # Check if maintenance mode is enabled
        maintenance_mode = getattr(settings, 'MAINTENANCE_MODE', False)
        
        if maintenance_mode:
            # Only allow admin users during maintenance
            return request.user.is_staff
        
        return True