from rest_framework import serializers
from .models import CustomerQuery, QueryResponse, Appointment, EmailTemplate, EmailLog
from users.serializers import UserSerializer
from events.serializers import EventSerializer

class EmailTemplateSerializer(serializers.ModelSerializer):
    """Serializer for EmailTemplate model"""
    
    class Meta:
        model = EmailTemplate
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

class CustomerQueryCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating customer queries (public endpoint)"""
    
    class Meta:
        model = CustomerQuery
        fields = ['name', 'email', 'phone', 'subject', 'message', 'event']
        
    def validate_email(self, value):
        """Validate email format"""
        if not value:
            raise serializers.ValidationError("Email is required")
        return value.lower()
    
    def validate_subject(self, value):
        """Validate subject length"""
        if len(value.strip()) < 5:
            raise serializers.ValidationError("Subject must be at least 5 characters long")
        return value.strip()
    
    def validate_message(self, value):
        """Validate message length"""
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Message must be at least 10 characters long")
        return value.strip()

class CustomerQuerySerializer(serializers.ModelSerializer):
    """Serializer for CustomerQuery model"""
    assigned_to = UserSerializer(read_only=True)
    event = EventSerializer(read_only=True)
    responses_count = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomerQuery
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'resolved_at']
    
    def get_responses_count(self, obj):
        """Get count of responses for this query"""
        return obj.responses.filter(is_internal=False).count()

class QueryResponseSerializer(serializers.ModelSerializer):
    """Serializer for QueryResponse model"""
    responder = UserSerializer(read_only=True)
    query_subject = serializers.CharField(source='query.subject', read_only=True)
    
    class Meta:
        model = QueryResponse
        fields = '__all__'
        read_only_fields = ['created_at', 'responder', 'email_sent']
    
    def validate_message(self, value):
        """Validate response message"""
        if len(value.strip()) < 5:
            raise serializers.ValidationError("Response message must be at least 5 characters long")
        return value.strip()

class AppointmentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating appointments (public endpoint)"""
    
    class Meta:
        model = Appointment
        fields = [
            'name', 'email', 'phone', 'appointment_type', 'preferred_date',
            'preferred_time', 'duration_minutes', 'message', 'event'
        ]
    
    def validate_email(self, value):
        """Validate email format"""
        if not value:
            raise serializers.ValidationError("Email is required")
        return value.lower()
    
    def validate_phone(self, value):
        """Validate phone number"""
        if not value:
            raise serializers.ValidationError("Phone number is required")
        # Remove any non-digit characters for validation
        digits_only = ''.join(filter(str.isdigit, value))
        if len(digits_only) < 10:
            raise serializers.ValidationError("Phone number must be at least 10 digits")
        return value
    
    def validate_preferred_date(self, value):
        """Validate preferred date is not in the past"""
        from django.utils import timezone
        if value < timezone.now().date():
            raise serializers.ValidationError("Preferred date cannot be in the past")
        return value
    
    def validate_duration_minutes(self, value):
        """Validate duration is reasonable"""
        if value < 15:
            raise serializers.ValidationError("Appointment duration must be at least 15 minutes")
        if value > 480:  # 8 hours
            raise serializers.ValidationError("Appointment duration cannot exceed 8 hours")
        return value

class AppointmentSerializer(serializers.ModelSerializer):
    """Serializer for Appointment model"""
    assigned_to = UserSerializer(read_only=True)
    event = EventSerializer(read_only=True)
    appointment_type_display = serializers.CharField(source='get_appointment_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Appointment
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'reminder_sent']
    
    def validate_confirmed_date(self, value):
        """Validate confirmed date is not in the past"""
        if value:
            from django.utils import timezone
            if value < timezone.now().date():
                raise serializers.ValidationError("Confirmed date cannot be in the past")
        return value

class EmailLogSerializer(serializers.ModelSerializer):
    """Serializer for EmailLog model"""
    template_used = EmailTemplateSerializer(read_only=True)
    query = CustomerQuerySerializer(read_only=True)
    appointment = AppointmentSerializer(read_only=True)
    email_type_display = serializers.CharField(source='get_email_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = EmailLog
        fields = '__all__'
        read_only_fields = ['created_at', 'sent_at']

class EmailStatsSerializer(serializers.Serializer):
    """Serializer for email statistics"""
    total_emails = serializers.IntegerField()
    sent_emails = serializers.IntegerField()
    failed_emails = serializers.IntegerField()
    pending_emails = serializers.IntegerField()
    success_rate = serializers.FloatField()
    
    # Email type breakdown
    query_responses = serializers.IntegerField()
    appointment_confirmations = serializers.IntegerField()
    appointment_reminders = serializers.IntegerField()
    welcome_emails = serializers.IntegerField()
    custom_emails = serializers.IntegerField()

class QueryStatsSerializer(serializers.Serializer):
    """Serializer for query statistics"""
    total_queries = serializers.IntegerField()
    pending_queries = serializers.IntegerField()
    in_progress_queries = serializers.IntegerField()
    resolved_queries = serializers.IntegerField()
    closed_queries = serializers.IntegerField()
    
    # Priority breakdown
    urgent_queries = serializers.IntegerField()
    high_priority_queries = serializers.IntegerField()
    medium_priority_queries = serializers.IntegerField()
    low_priority_queries = serializers.IntegerField()
    
    # Response time stats
    avg_response_time_hours = serializers.FloatField()

class AppointmentStatsSerializer(serializers.Serializer):
    """Serializer for appointment statistics"""
    total_appointments = serializers.IntegerField()
    pending_appointments = serializers.IntegerField()
    confirmed_appointments = serializers.IntegerField()
    cancelled_appointments = serializers.IntegerField()
    completed_appointments = serializers.IntegerField()
    no_show_appointments = serializers.IntegerField()
    
    # Type breakdown
    consultation_appointments = serializers.IntegerField()
    photoshoot_appointments = serializers.IntegerField()
    event_planning_appointments = serializers.IntegerField()
    album_delivery_appointments = serializers.IntegerField()
    other_appointments = serializers.IntegerField()