from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'queries', views.CustomerQueryViewSet)
router.register(r'responses', views.QueryResponseViewSet)
router.register(r'appointments', views.AppointmentViewSet)
router.register(r'templates', views.EmailTemplateViewSet)
router.register(r'logs', views.EmailLogViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    
    # Additional custom endpoints
    path('api/stats/emails/', views.EmailStatsView.as_view(), name='email-stats'),
    path('api/stats/queries/', views.QueryStatsView.as_view(), name='query-stats'),
    path('api/stats/appointments/', views.AppointmentStatsView.as_view(), name='appointment-stats'),
    
    # Email sending endpoints
    path('api/send-custom-email/', views.SendCustomEmailView.as_view(), name='send-custom-email'),
    path('api/send-welcome-email/', views.SendWelcomeEmailView.as_view(), name='send-welcome-email'),
    
    # Bulk operations
    path('api/queries/bulk-assign/', views.BulkAssignQueriesView.as_view(), name='bulk-assign-queries'),
    path('api/appointments/bulk-confirm/', views.BulkConfirmAppointmentsView.as_view(), name='bulk-confirm-appointments'),
    path('api/appointments/send-reminders/', views.SendAppointmentRemindersView.as_view(), name='send-appointment-reminders'),
]

app_name = 'email_service'