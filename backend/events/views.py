from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import Event, Photo, Video, Reel
from .serializers import (
    EventSerializer,
    EventDetailSerializer,
    PhotoSerializer,
    VideoSerializer,
    ReelSerializer
)


class EventViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing and editing Event instances."""
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_published', 'is_featured', 'event_date']
    search_fields = ['title', 'description', 'event_id']
    ordering_fields = ['event_date', 'created_at', 'title']
    ordering = ['-event_date']
    
    def get_serializer_class(self):
        """Return the appropriate serializer class based on the action."""
        if self.action == 'retrieve':
            return EventDetailSerializer
        return EventSerializer
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def published(self, request):
        """Get all published events."""
        events = Event.objects.filter(is_published=True)
        serializer = self.get_serializer(events, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def featured(self, request):
        """Get all featured events."""
        events = Event.objects.filter(is_featured=True, is_published=True)
        serializer = self.get_serializer(events, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], permission_classes=[permissions.AllowAny])
    def public_detail(self, request, pk=None):
        """Get event details for public access (without sensitive data)."""
        event = get_object_or_404(Event, pk=pk, is_published=True)
        
        # Create a copy of the serializer data without sensitive fields
        serializer = EventDetailSerializer(event, context={'request': request})
        data = serializer.data.copy()
        
        # Remove sensitive fields for public access
        data.pop('password', None)
        data.pop('clients', None)
        
        return Response(data)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.AllowAny])
    def verify_access(self, request, pk=None):
        """Verify access to an event using event ID and password."""
        event = get_object_or_404(Event, pk=pk)
        password = request.data.get('password')
        
        # Check if the event is password protected and if the password matches
        if event.is_password_protected and event.password != password:
            return Response(
                {"detail": "Invalid password."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Check if the event has expired
        if event.is_expired:
            return Response(
                {"detail": "This event has expired."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Return event details with access granted
        serializer = EventDetailSerializer(event, context={'request': request})
        data = serializer.data.copy()
        data['access_granted'] = True
        
        return Response(data)


class PhotoViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing and editing Photo instances."""
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['event', 'is_featured']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'title']
    ordering = ['created_at']
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def by_event(self, request):
        """Get photos by event ID."""
        event_id = request.query_params.get('event_id')
        if not event_id:
            return Response(
                {"detail": "event_id parameter is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            event = Event.objects.get(event_id=event_id, is_published=True)
            photos = Photo.objects.filter(event=event)
            serializer = self.get_serializer(photos, many=True)
            return Response(serializer.data)
        except Event.DoesNotExist:
            return Response(
                {"detail": "Event not found."},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def featured(self, request):
        """Get all featured photos from published events."""
        photos = Photo.objects.filter(is_featured=True, event__is_published=True)
        serializer = self.get_serializer(photos, many=True)
        return Response(serializer.data)


class VideoViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing and editing Video instances."""
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['event', 'is_featured']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'title']
    ordering = ['created_at']
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def by_event(self, request):
        """Get videos by event ID."""
        event_id = request.query_params.get('event_id')
        if not event_id:
            return Response(
                {"detail": "event_id parameter is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            event = Event.objects.get(event_id=event_id, is_published=True)
            videos = Video.objects.filter(event=event)
            serializer = self.get_serializer(videos, many=True)
            return Response(serializer.data)
        except Event.DoesNotExist:
            return Response(
                {"detail": "Event not found."},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def featured(self, request):
        """Get all featured videos from published events."""
        videos = Video.objects.filter(is_featured=True, event__is_published=True)
        serializer = self.get_serializer(videos, many=True)
        return Response(serializer.data)


class ReelViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing and editing Reel instances."""
    queryset = Reel.objects.all()
    serializer_class = ReelSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['event', 'is_featured']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'title']
    ordering = ['-created_at']
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def public(self, request):
        """Get all reels from published events for public viewing."""
        reels = Reel.objects.filter(event__is_published=True)
        serializer = self.get_serializer(reels, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def featured(self, request):
        """Get all featured reels from published events."""
        reels = Reel.objects.filter(is_featured=True, event__is_published=True)
        serializer = self.get_serializer(reels, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def by_event(self, request):
        """Get reels by event ID."""
        event_id = request.query_params.get('event_id')
        if not event_id:
            return Response(
                {"detail": "event_id parameter is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            event = Event.objects.get(event_id=event_id, is_published=True)
            reels = Reel.objects.filter(event=event)
            serializer = self.get_serializer(reels, many=True)
            return Response(serializer.data)
        except Event.DoesNotExist:
            return Response(
                {"detail": "Event not found."},
                status=status.HTTP_404_NOT_FOUND
            )