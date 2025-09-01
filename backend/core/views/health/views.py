from django.db import connection
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)

class HealthCheckView(APIView):
    """
    API endpoint for health checks.
    This endpoint is used by monitoring tools to verify the application status.
    """
    permission_classes = []
    authentication_classes = []
    
    def get(self, request):
        health_data = {
            'status': 'healthy',
            'database': 'unavailable',
            'version': getattr(settings, 'APP_VERSION', 'unknown')
        }
        
        # Check database connection
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
                cursor.fetchone()
            health_data['database'] = 'connected'
        except Exception as e:
            health_data['status'] = 'unhealthy'
            health_data['database'] = 'disconnected'
            health_data['database_error'] = str(e)
            logger.error(f"Health check database error: {e}")
            return Response(health_data, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        # Add additional health checks here as needed
        # For example: cache, storage, external services, etc.
        
        return Response(health_data, status=status.HTTP_200_OK)