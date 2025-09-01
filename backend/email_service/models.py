from django.db import models
from django.contrib.auth import get_user_model
from events.models import Event

User = get_user_model()

class EmailTemplate(models.Model):
    """Email templates for different types of communications"""
    TEMPLATE_TYPES = [
        ('query_response', 'Query Response'),
        ('appointment_confirmation', 'Appointment Confirmation'),
        ('appointment_reminder', 'Appointment Reminder'),
        ('event_notification', 'Event Notification'),
        ('welcome', 'Welcome Email'),
    ]
    
    name = models.CharField(max_length=100)
    template_type = models.CharField(max_length=50, choices=TEMPLATE_TYPES)
    subject = models.CharField(max_length=200)
    html_content = models.TextField()
    text_content = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['template_type', 'is_active']
    
    def __str__(self):
        return f"{self.name} ({self.template_type})"

class CustomerQuery(models.Model):
    """Customer queries and inquiries"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.subject}"

class QueryResponse(models.Model):
    """Responses to customer queries"""
    query = models.ForeignKey(CustomerQuery, on_delete=models.CASCADE, related_name='responses')
    responder = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_internal = models.BooleanField(default=False)  # Internal notes vs customer-facing responses
    email_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Response to {self.query.subject}"

class Appointment(models.Model):
    """Appointment bookings"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
        ('no_show', 'No Show'),
    ]
    
    APPOINTMENT_TYPES = [
        ('consultation', 'Consultation'),
        ('photoshoot', 'Photoshoot'),
        ('event_planning', 'Event Planning'),
        ('album_delivery', 'Album Delivery'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    appointment_type = models.CharField(max_length=50, choices=APPOINTMENT_TYPES)
    preferred_date = models.DateField()
    preferred_time = models.TimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    confirmed_date = models.DateField(null=True, blank=True)
    confirmed_time = models.TimeField(null=True, blank=True)
    location = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    reminder_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['preferred_date', 'preferred_time']
    
    def __str__(self):
        return f"{self.name} - {self.appointment_type} on {self.preferred_date}"

class EmailLog(models.Model):
    """Log of all emails sent"""
    EMAIL_TYPES = [
        ('query_response', 'Query Response'),
        ('appointment_confirmation', 'Appointment Confirmation'),
        ('appointment_reminder', 'Appointment Reminder'),
        ('event_notification', 'Event Notification'),
        ('welcome', 'Welcome Email'),
        ('custom', 'Custom Email'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('bounced', 'Bounced'),
    ]
    
    recipient_email = models.EmailField()
    recipient_name = models.CharField(max_length=100, blank=True)
    subject = models.CharField(max_length=200)
    email_type = models.CharField(max_length=50, choices=EMAIL_TYPES)
    template_used = models.ForeignKey(EmailTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    sent_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    query = models.ForeignKey(CustomerQuery, on_delete=models.SET_NULL, null=True, blank=True)
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.email_type} to {self.recipient_email}"
