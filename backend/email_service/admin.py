from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import EmailTemplate, CustomerQuery, QueryResponse, Appointment, EmailLog
from .utils import EmailService

@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'template_type', 'is_active', 'created_at', 'updated_at']
    list_filter = ['template_type', 'is_active', 'created_at']
    search_fields = ['name', 'subject']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'template_type', 'is_active')
        }),
        ('Email Content', {
            'fields': ('subject', 'html_content', 'text_content')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['activate_templates', 'deactivate_templates']
    
    def activate_templates(self, request, queryset):
        """Activate selected templates"""
        for template in queryset:
            # Deactivate other templates of the same type
            EmailTemplate.objects.filter(
                template_type=template.template_type
            ).exclude(id=template.id).update(is_active=False)
            
            # Activate this template
            template.is_active = True
            template.save()
        
        self.message_user(request, f"{queryset.count()} templates activated successfully.")
    activate_templates.short_description = "Activate selected templates"
    
    def deactivate_templates(self, request, queryset):
        """Deactivate selected templates"""
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} templates deactivated successfully.")
    deactivate_templates.short_description = "Deactivate selected templates"

class QueryResponseInline(admin.TabularInline):
    model = QueryResponse
    extra = 0
    readonly_fields = ['created_at', 'email_sent']
    fields = ['responder', 'message', 'is_internal', 'email_sent', 'created_at']

@admin.register(CustomerQuery)
class CustomerQueryAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'email', 'subject', 'status', 'priority', 
        'assigned_to', 'created_at', 'responses_count'
    ]
    list_filter = ['status', 'priority', 'created_at', 'assigned_to']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['created_at', 'updated_at', 'resolved_at']
    inlines = [QueryResponseInline]
    
    fieldsets = (
        ('Customer Information', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Query Details', {
            'fields': ('subject', 'message', 'event')
        }),
        ('Management', {
            'fields': ('status', 'priority', 'assigned_to')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'resolved_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['assign_to_me', 'mark_resolved', 'mark_in_progress']
    
    def responses_count(self, obj):
        """Display count of responses"""
        count = obj.responses.count()
        if count > 0:
            url = reverse('admin:email_service_queryresponse_changelist')
            return format_html(
                '<a href="{}?query__id__exact={}">{} responses</a>',
                url, obj.id, count
            )
        return '0 responses'
    responses_count.short_description = 'Responses'
    
    def assign_to_me(self, request, queryset):
        """Assign selected queries to current user"""
        queryset.update(assigned_to=request.user, status='in_progress')
        self.message_user(request, f"{queryset.count()} queries assigned to you.")
    assign_to_me.short_description = "Assign to me"
    
    def mark_resolved(self, request, queryset):
        """Mark selected queries as resolved"""
        queryset.update(status='resolved', resolved_at=timezone.now())
        self.message_user(request, f"{queryset.count()} queries marked as resolved.")
    mark_resolved.short_description = "Mark as resolved"
    
    def mark_in_progress(self, request, queryset):
        """Mark selected queries as in progress"""
        queryset.update(status='in_progress')
        self.message_user(request, f"{queryset.count()} queries marked as in progress.")
    mark_in_progress.short_description = "Mark as in progress"

@admin.register(QueryResponse)
class QueryResponseAdmin(admin.ModelAdmin):
    list_display = [
        'query_subject', 'responder', 'is_internal', 
        'email_sent', 'created_at'
    ]
    list_filter = ['is_internal', 'email_sent', 'created_at', 'responder']
    search_fields = ['query__subject', 'message', 'responder__email']
    readonly_fields = ['created_at', 'email_sent']
    
    def query_subject(self, obj):
        """Display query subject with link"""
        url = reverse('admin:email_service_customerquery_change', args=[obj.query.id])
        return format_html('<a href="{}">{}</a>', url, obj.query.subject)
    query_subject.short_description = 'Query Subject'

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'email', 'appointment_type', 'preferred_date', 
        'preferred_time', 'status', 'assigned_to', 'reminder_sent'
    ]
    list_filter = [
        'appointment_type', 'status', 'preferred_date', 
        'assigned_to', 'reminder_sent'
    ]
    search_fields = ['name', 'email', 'phone']
    readonly_fields = ['created_at', 'updated_at', 'reminder_sent']
    
    fieldsets = (
        ('Customer Information', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Appointment Details', {
            'fields': (
                'appointment_type', 'preferred_date', 'preferred_time',
                'duration_minutes', 'message', 'event'
            )
        }),
        ('Confirmation Details', {
            'fields': (
                'status', 'confirmed_date', 'confirmed_time',
                'location', 'notes', 'assigned_to'
            )
        }),
        ('System Information', {
            'fields': ('reminder_sent', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = [
        'confirm_appointments', 'send_reminders', 
        'assign_to_me', 'mark_completed'
    ]
    
    def confirm_appointments(self, request, queryset):
        """Confirm selected appointments"""
        confirmed_count = 0
        for appointment in queryset.filter(status='pending'):
            appointment.status = 'confirmed'
            if not appointment.confirmed_date:
                appointment.confirmed_date = appointment.preferred_date
            if not appointment.confirmed_time:
                appointment.confirmed_time = appointment.preferred_time
            appointment.save()
            
            # Send confirmation email
            EmailService.send_appointment_confirmation(appointment)
            confirmed_count += 1
        
        self.message_user(
            request, 
            f"{confirmed_count} appointments confirmed and emails sent."
        )
    confirm_appointments.short_description = "Confirm and send emails"
    
    def send_reminders(self, request, queryset):
        """Send reminder emails for confirmed appointments"""
        reminder_count = 0
        for appointment in queryset.filter(status='confirmed'):
            if EmailService.send_appointment_reminder(appointment):
                appointment.reminder_sent = True
                appointment.save()
                reminder_count += 1
        
        self.message_user(
            request, 
            f"{reminder_count} reminder emails sent successfully."
        )
    send_reminders.short_description = "Send reminder emails"
    
    def assign_to_me(self, request, queryset):
        """Assign selected appointments to current user"""
        queryset.update(assigned_to=request.user)
        self.message_user(request, f"{queryset.count()} appointments assigned to you.")
    assign_to_me.short_description = "Assign to me"
    
    def mark_completed(self, request, queryset):
        """Mark selected appointments as completed"""
        queryset.update(status='completed')
        self.message_user(request, f"{queryset.count()} appointments marked as completed.")
    mark_completed.short_description = "Mark as completed"

@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = [
        'recipient_email', 'subject', 'email_type', 
        'status', 'sent_at', 'created_at'
    ]
    list_filter = ['email_type', 'status', 'sent_at', 'created_at']
    search_fields = ['recipient_email', 'recipient_name', 'subject']
    readonly_fields = [
        'created_at', 'sent_at', 'recipient_email', 'recipient_name',
        'subject', 'email_type', 'status', 'error_message'
    ]
    
    def has_add_permission(self, request):
        """Disable adding email logs manually"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Make email logs read-only"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Allow deletion for cleanup"""
        return request.user.is_superuser
