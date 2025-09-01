from django.urls import path
from . import views

urlpatterns = [
    path('stats/', views.dashboard_stats, name='dashboard-stats'),
    path('analytics/events/', views.event_analytics, name='event-analytics'),
    path('analytics/events/<int:event_id>/', views.event_analytics, name='event-analytics-detail'),
    path('analytics/media/', views.media_analytics, name='media-analytics'),
    path('analytics/users/', views.user_analytics, name='user-analytics'),
]