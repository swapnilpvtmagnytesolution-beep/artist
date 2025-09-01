from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'events', views.EventViewSet)
router.register(r'photos', views.PhotoViewSet)
router.register(r'videos', views.VideoViewSet)
router.register(r'reels', views.ReelViewSet)

urlpatterns = [
    path('', include(router.urls)),
]