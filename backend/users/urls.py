from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    UserViewSet,
    CustomTokenObtainPairView,
    EventClientViewSet,
    EventLoginView
)

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'clients', EventClientViewSet)

# The API URLs are determined automatically by the router
urlpatterns = [
    # JWT authentication
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Event login
    path('event-login/', EventLoginView.as_view(), name='event_login'),
    
    # Include the router URLs
    path('', include(router.urls)),
]