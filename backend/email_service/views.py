from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from django.db.models import Q, Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import CustomerQuery, QueryResponse, Appointment, EmailTemplate, EmailLog
from .serializers import (
    CustomerQuerySerializer, QueryResponseSerializer, AppointmentSerializer,
    EmailTemplateSerializer, EmailLogSerializer, CustomerQueryCreateSerializer,
    AppointmentCreateSerializer
)
from .utils import EmailService
import logging

logger = logging.getLogger(__name__)

class CustomerQueryViewSet(viewsets.ModelViewSet):
    """ViewSet for managing customer queries"""
    queryset = CustomerQuery.objects.all()
    serializer_class = CustomerQuerySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'priority', 'event', 'assigned_to']
    search_fields = ['name', 'email', 'subject', 'message']
    ordering_fields = ['created_at', 'updated_at', 'priority']
    ordering = ['-created_at']


# Statistics Views
class EmailStatsView(APIView):
    """View for email statistics"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get email statistics"""
        total_emails = EmailLog.objects.count()
        sent_emails = EmailLog.objects.filter(status='sent').count()
        failed_emails = EmailLog.objects.filter(status='failed').count()
        pending_emails = EmailLog.objects.filter(status='pending').count()
        
        # Email types breakdown
        email_types = EmailLog.objects.values('email_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Recent activity (last 30 days)
        thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
        recent_emails = EmailLog.objects.filter(
            created_at__gte=thirty_days_ago
        ).count()
        
        return Response({
            'total_emails': total_emails,
            'sent_emails': sent_emails,
            'failed_emails': failed_emails,
            'pending_emails': pending_emails,
            'success_rate': (sent_emails / total_emails * 100) if total_emails > 0 else 0,
            'email_types': email_types,
            'recent_activity': recent_emails
        })


class QueryStatsView(APIView):
    """View for query statistics"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get query statistics"""
        total_queries = CustomerQuery.objects.count()
        pending_queries = CustomerQuery.objects.filter(status='pending').count()
        in_progress_queries = CustomerQuery.objects.filter(status='in_progress').count()
        resolved_queries = CustomerQuery.objects.filter(status='resolved').count()
        
        # Priority breakdown
        priority_breakdown = CustomerQuery.objects.values('priority').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Recent queries (last 30 days)
        thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
        recent_queries = CustomerQuery.objects.filter(
            created_at__gte=thirty_days_ago
        ).count()
        
        # Average response time (for resolved queries)
        resolved_with_responses = CustomerQuery.objects.filter(
            status='resolved',
            responses__isnull=False
        ).distinct()
        
        return Response({
            'total_queries': total_queries,
            'pending_queries': pending_queries,
            'in_progress_queries': in_progress_queries,
            'resolved_queries': resolved_queries,
            'resolution_rate': (resolved_queries / total_queries * 100) if total_queries > 0 else 0,
            'priority_breakdown': priority_breakdown,
            'recent_activity': recent_queries
        })


class AppointmentStatsView(APIView):
    """View for appointment statistics"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get appointment statistics"""
        total_appointments = Appointment.objects.count()
        pending_appointments = Appointment.objects.filter(status='pending').count()
        confirmed_appointments = Appointment.objects.filter(status='confirmed').count()
        completed_appointments = Appointment.objects.filter(status='completed').count()
        cancelled_appointments = Appointment.objects.filter(status='cancelled').count()
        
        # Appointment types breakdown
        type_breakdown = Appointment.objects.values('appointment_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Recent appointments (last 30 days)
        thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
        recent_appointments = Appointment.objects.filter(
            created_at__gte=thirty_days_ago
        ).count()
        
        # Upcoming appointments (next 7 days)
        seven_days_ahead = timezone.now().date() + timezone.timedelta(days=7)
        upcoming_appointments = Appointment.objects.filter(
            preferred_date__lte=seven_days_ahead,
            preferred_date__gte=timezone.now().date(),
            status__in=['pending', 'confirmed']
        ).count()
        
        return Response({
            'total_appointments': total_appointments,
            'pending_appointments': pending_appointments,
            'confirmed_appointments': confirmed_appointments,
            'completed_appointments': completed_appointments,
            'cancelled_appointments': cancelled_appointments,
            'confirmation_rate': (confirmed_appointments / total_appointments * 100) if total_appointments > 0 else 0,
            'type_breakdown': type_breakdown,
            'recent_activity': recent_appointments,
            'upcoming_appointments': upcoming_appointments
        })


# Custom Email Views
class SendCustomEmailView(APIView):
    """View for sending custom emails"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Send a custom email"""
        recipient_email = request.data.get('recipient_email')
        recipient_name = request.data.get('recipient_name', '')
        subject = request.data.get('subject')
        message = request.data.get('message')
        
        if not all([recipient_email, subject, message]):
            return Response({
                'error': 'recipient_email, subject, and message are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        email_sent = EmailService.send_custom_email(
            recipient_email=recipient_email,
            recipient_name=recipient_name,
            subject=subject,
            message=message
        )
        
        return Response({
            'email_sent': email_sent,
            'message': 'Email sent successfully' if email_sent else 'Failed to send email'
        })


class SendWelcomeEmailView(APIView):
    """View for sending welcome emails"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Send a welcome email"""
        recipient_email = request.data.get('recipient_email')
        recipient_name = request.data.get('recipient_name', '')
        
        if not recipient_email:
            return Response({
                'error': 'recipient_email is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        email_sent = EmailService.send_welcome_email(
            recipient_email=recipient_email,
            recipient_name=recipient_name
        )
        
        return Response({
            'email_sent': email_sent,
            'message': 'Welcome email sent successfully' if email_sent else 'Failed to send welcome email'
        })


# Bulk Operation Views
class BulkAssignQueriesView(APIView):
    """View for bulk assigning queries"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Bulk assign queries to a user"""
        query_ids = request.data.get('query_ids', [])
        assigned_to_id = request.data.get('assigned_to_id')
        
        if not query_ids or not assigned_to_id:
            return Response({
                'error': 'query_ids and assigned_to_id are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            assigned_to = User.objects.get(id=assigned_to_id)
            
            updated_count = CustomerQuery.objects.filter(
                id__in=query_ids
            ).update(
                assigned_to=assigned_to,
                status='in_progress'
            )
            
            return Response({
                'updated_count': updated_count,
                'message': f'{updated_count} queries assigned successfully'
            })
            
        except User.DoesNotExist:
            return Response({
                'error': 'Invalid assigned_to_id'
            }, status=status.HTTP_400_BAD_REQUEST)


class BulkConfirmAppointmentsView(APIView):
    """View for bulk confirming appointments"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Bulk confirm appointments"""
        appointment_ids = request.data.get('appointment_ids', [])
        
        if not appointment_ids:
            return Response({
                'error': 'appointment_ids are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        confirmed_count = 0
        for appointment in Appointment.objects.filter(
            id__in=appointment_ids,
            status='pending'
        ):
            appointment.status = 'confirmed'
            if not appointment.confirmed_date:
                appointment.confirmed_date = appointment.preferred_date
            if not appointment.confirmed_time:
                appointment.confirmed_time = appointment.preferred_time
            appointment.save()
            
            # Send confirmation email
            EmailService.send_appointment_confirmation(appointment)
            confirmed_count += 1
        
        return Response({
            'confirmed_count': confirmed_count,
            'message': f'{confirmed_count} appointments confirmed and emails sent'
        })


class SendAppointmentRemindersView(APIView):
    """View for sending appointment reminders"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Send appointment reminders"""
        appointment_ids = request.data.get('appointment_ids', [])
        
        if not appointment_ids:
            # Send reminders for all confirmed appointments in the next 24 hours
            tomorrow = timezone.now().date() + timezone.timedelta(days=1)
            appointments = Appointment.objects.filter(
                status='confirmed',
                preferred_date=tomorrow,
                reminder_sent=False
            )
        else:
            appointments = Appointment.objects.filter(
                id__in=appointment_ids,
                status='confirmed'
            )
        
        reminder_count = 0
        for appointment in appointments:
            if EmailService.send_appointment_reminder(appointment):
                appointment.reminder_sent = True
                appointment.save()
                reminder_count += 1
        
        return Response({
            'reminder_count': reminder_count,
            'message': f'{reminder_count} reminder emails sent successfully'
        })
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CustomerQueryCreateSerializer
        return CustomerQuerySerializer
    
    def get_permissions(self):
        """Allow anonymous users to create queries"""
        if self.action == 'create':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['post'])
    def respond(self, request, pk=None):
        """Respond to a customer query"""
        query = self.get_object()
        response_message = request.data.get('message', '')
        is_internal = request.data.get('is_internal', False)
        
        if not response_message:
            return Response(
                {'error': 'Response message is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create response record
        response_obj = QueryResponse.objects.create(
            query=query,
            responder=request.user,
            message=response_message,
            is_internal=is_internal
        )
        
        # Send email if not internal
        if not is_internal:
            email_sent = EmailService.send_query_response(query, response_message)
            response_obj.email_sent = email_sent
            response_obj.save()
            
            if email_sent:
                # Update query status
                query.status = 'resolved'
                query.resolved_at = timezone.now()
                query.save()
        
        serializer = QueryResponseSerializer(response_obj)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['patch'])
    def assign(self, request, pk=None):
        """Assign query to a user"""
        query = self.get_object()
        assigned_to_id = request.data.get('assigned_to')
        
        if assigned_to_id:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                assigned_user = User.objects.get(id=assigned_to_id)
                query.assigned_to = assigned_user
                query.status = 'in_progress'
                query.save()
                
                serializer = self.get_serializer(query)
                return Response(serializer.data)
            except User.DoesNotExist:
                return Response(
                    {'error': 'User not found'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            query.assigned_to = None
            query.save()
            
            serializer = self.get_serializer(query)
            return Response(serializer.data)

class QueryResponseViewSet(viewsets.ModelViewSet):
    """ViewSet for managing query responses"""
    queryset = QueryResponse.objects.all()
    serializer_class = QueryResponseSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['query', 'responder', 'is_internal', 'email_sent']
    ordering = ['created_at']

class AppointmentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing appointments"""
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'appointment_type', 'assigned_to', 'event']
    search_fields = ['name', 'email', 'phone']
    ordering_fields = ['preferred_date', 'preferred_time', 'created_at']
    ordering = ['preferred_date', 'preferred_time']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return AppointmentCreateSerializer
        return AppointmentSerializer
    
    def get_permissions(self):
        """Allow anonymous users to create appointments"""
        if self.action == 'create':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirm an appointment"""
        appointment = self.get_object()
        confirmed_date = request.data.get('confirmed_date')
        confirmed_time = request.data.get('confirmed_time')
        location = request.data.get('location', '')
        notes = request.data.get('notes', '')
        
        # Update appointment
        appointment.status = 'confirmed'
        if confirmed_date:
            appointment.confirmed_date = confirmed_date
        if confirmed_time:
            appointment.confirmed_time = confirmed_time
        if location:
            appointment.location = location
        if notes:
            appointment.notes = notes
        
        appointment.save()
        
        # Send confirmation email
        email_sent = EmailService.send_appointment_confirmation(appointment)
        
        serializer = self.get_serializer(appointment)
        response_data = serializer.data
        response_data['email_sent'] = email_sent
        
        return Response(response_data)
    
    @action(detail=True, methods=['post'])
    def send_reminder(self, request, pk=None):
        """Send reminder email for appointment"""
        appointment = self.get_object()
        
        if appointment.status != 'confirmed':
            return Response(
                {'error': 'Can only send reminders for confirmed appointments'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        email_sent = EmailService.send_appointment_reminder(appointment)
        
        if email_sent:
            appointment.reminder_sent = True
            appointment.save()
        
        return Response({
            'email_sent': email_sent,
            'message': 'Reminder sent successfully' if email_sent else 'Failed to send reminder'
        })
    
    @action(detail=True, methods=['patch'])
    def cancel(self, request, pk=None):
        """Cancel an appointment"""
        appointment = self.get_object()
        appointment.status = 'cancelled'
        appointment.save()
        
        serializer = self.get_serializer(appointment)
        return Response(serializer.data)

class EmailTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for managing email templates"""
    queryset = EmailTemplate.objects.all()
    serializer_class = EmailTemplateSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['template_type', 'is_active']
    search_fields = ['name', 'subject']
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a template (deactivate others of same type)"""
        template = self.get_object()
        
        # Deactivate other templates of the same type
        EmailTemplate.objects.filter(
            template_type=template.template_type
        ).update(is_active=False)
        
        # Activate this template
        template.is_active = True
        template.save()
        
        serializer = self.get_serializer(template)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def test_send(self, request, pk=None):
        """Send a test email using this template"""
        template = self.get_object()
        test_email = request.data.get('test_email')
        
        if not test_email:
            return Response(
                {'error': 'Test email address is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Test context
        test_context = {
            'recipient_name': 'Test User',
            'query_subject': 'Test Query',
            'query_message': 'This is a test query message',
            'response_message': 'This is a test response message',
            'appointment_type': 'Test Appointment',
            'appointment_date': timezone.now().date(),
            'appointment_time': timezone.now().time(),
            'location': 'Test Location',
        }
        
        email_sent = EmailService.send_templated_email(
            template_type=template.template_type,
            recipient_email=test_email,
            recipient_name='Test User',
            context=test_context
        )
        
        return Response({
            'email_sent': email_sent,
            'message': 'Test email sent successfully' if email_sent else 'Failed to send test email'
        })

class EmailLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing email logs"""
    queryset = EmailLog.objects.all()
    serializer_class = EmailLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['email_type', 'status', 'template_used']
    search_fields = ['recipient_email', 'recipient_name', 'subject']
    ordering_fields = ['created_at', 'sent_at']
    ordering = ['-created_at']
