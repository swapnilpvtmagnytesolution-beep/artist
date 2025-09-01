from rest_framework import viewsets, permissions, status, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model

from .models import EventClient
from .serializers import (
    UserSerializer, 
    CustomTokenObtainPairSerializer,
    EventClientSerializer,
    EventLoginSerializer
)
from events.models import Event

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing and editing User instances."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """Get the current user's profile."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put', 'patch'], permission_classes=[permissions.IsAuthenticated])
    def update_me(self, request):
        """Update the current user's profile."""
        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom token view that uses our enhanced token serializer."""
    serializer_class = CustomTokenObtainPairSerializer


class EventClientViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing and editing EventClient instances."""
    queryset = EventClient.objects.all()
    serializer_class = EventClientSerializer
    permission_classes = [permissions.IsAdminUser]


class EventLoginView(generics.GenericAPIView):
    """View for event login using event ID and password."""
    serializer_class = EventLoginSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        """Handle event login."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        event_id = serializer.validated_data['event_id']
        password = serializer.validated_data['password']
        
        try:
            event = Event.objects.get(event_id=event_id)
            
            # Check if the event is password protected and if the password matches
            if event.is_password_protected and event.password != password:
                return Response(
                    {"detail": "Invalid event ID or password."},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # Check if the event has expired
            if event.is_expired:
                return Response(
                    {"detail": "This event has expired."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Return event details
            from events.serializers import EventSerializer
            event_data = EventSerializer(event).data
            
            return Response({
                "event": event_data,
                "access_granted": True
            })
            
        except Event.DoesNotExist:
            return Response(
                {"detail": "Invalid event ID or password."},
                status=status.HTTP_401_UNAUTHORIZED
            )