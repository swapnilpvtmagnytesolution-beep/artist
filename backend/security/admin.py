from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.db.models import Count, Q
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    SecurityEvent, AuditLog, IPWhitelist, IPBlacklist,
    RateLimitRule, SessionSecurity
)


@admin.register(SecurityEvent)
class SecurityEventAdmin(admin.ModelAdmin):
    list_display = [
        'event_type', 'severity', 'user', 'ip_address',
        'timestamp', 'resolved', 'colored_severity'
    ]
    list_filter = [
        'event_type', 'severity', 'resolved', 'timestamp',
        ('user', admin.RelatedOnlyFieldListFilter)
    ]
    search_fields = ['ip_address', 'user__username', 'user__email', 'details']
    readonly_fields = ['timestamp', 'details_formatted']
    date_hierarchy = 'timestamp'
    actions = ['mark_resolved', 'mark_unresolved']
    
    fieldsets = (
        ('Event Information', {
            'fields': ('event_type', 'severity', 'timestamp', 'details_formatted')
        }),
        ('Request Information', {
            'fields': ('user', 'ip_address', 'user_agent', 'path', 'method')
        }),
        ('Resolution', {
            'fields': ('resolved', 'resolved_by', 'resolved_at', 'notes')
        }),
    )
    
    def colored_severity(self, obj):
        colors = {
            'low': 'green',
            'medium': 'orange',
            'high': 'red',
            'critical': 'darkred'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.severity, 'black'),
            obj.get_severity_display()
        )
    colored_severity.short_description = 'Severity'
    
    def details_formatted(self, obj):
        import json
        if obj.details:
            formatted = json.dumps(obj.details, indent=2)
            return format_html('<pre>{}</pre>', formatted)
        return 'No details'
    details_formatted.short_description = 'Details'
    
    def mark_resolved(self, request, queryset):
        updated = queryset.update(
            resolved=True,
            resolved_by=request.user,
            resolved_at=timezone.now()
        )
        self.message_user(request, f'{updated} events marked as resolved.')
    mark_resolved.short_description = 'Mark selected events as resolved'
    
    def mark_unresolved(self, request, queryset):
        updated = queryset.update(
            resolved=False,
            resolved_by=None,
            resolved_at=None
        )
        self.message_user(request, f'{updated} events marked as unresolved.')
    mark_unresolved.short_description = 'Mark selected events as unresolved'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'resolved_by')


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'action', 'resource_type', 'resource_name',
        'ip_address', 'timestamp', 'success', 'success_icon'
    ]
    list_filter = [
        'action', 'resource_type', 'success', 'timestamp',
        ('user', admin.RelatedOnlyFieldListFilter)
    ]
    search_fields = [
        'user__username', 'user__email', 'resource_name',
        'ip_address', 'details'
    ]
    readonly_fields = ['timestamp', 'details_formatted']
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Action Information', {
            'fields': ('user', 'action', 'timestamp', 'success')
        }),
        ('Resource Information', {
            'fields': ('resource_type', 'resource_id', 'resource_name')
        }),
        ('Request Information', {
            'fields': ('ip_address', 'user_agent')
        }),
        ('Details', {
            'fields': ('details_formatted', 'error_message'),
            'classes': ('collapse',)
        }),
    )
    
    def success_icon(self, obj):
        if obj.success:
            return format_html(
                '<span style="color: green;">✓</span>'
            )
        else:
            return format_html(
                '<span style="color: red;">✗</span>'
            )
    success_icon.short_description = ''
    
    def details_formatted(self, obj):
        import json
        if obj.details:
            formatted = json.dumps(obj.details, indent=2)
            return format_html('<pre>{}</pre>', formatted)
        return 'No details'
    details_formatted.short_description = 'Details'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(IPWhitelist)
class IPWhitelistAdmin(admin.ModelAdmin):
    list_display = [
        'ip_address', 'description', 'is_active',
        'created_by', 'created_at', 'expires_at', 'status_icon'
    ]
    list_filter = ['is_active', 'created_at', 'expires_at']
    search_fields = ['ip_address', 'description']
    readonly_fields = ['created_at']
    actions = ['activate', 'deactivate']
    
    def status_icon(self, obj):
        if obj.is_expired():
            return format_html(
                '<span style="color: orange;">⏰ Expired</span>'
            )
        elif obj.is_active:
            return format_html(
                '<span style="color: green;">✓ Active</span>'
            )
        else:
            return format_html(
                '<span style="color: red;">✗ Inactive</span>'
            )
    status_icon.short_description = 'Status'
    
    def activate(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} entries activated.')
    activate.short_description = 'Activate selected entries'
    
    def deactivate(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} entries deactivated.')
    deactivate.short_description = 'Deactivate selected entries'


@admin.register(IPBlacklist)
class IPBlacklistAdmin(admin.ModelAdmin):
    list_display = [
        'ip_address', 'reason', 'is_active', 'auto_generated',
        'created_by', 'created_at', 'expires_at', 'status_icon'
    ]
    list_filter = ['is_active', 'auto_generated', 'created_at', 'expires_at']
    search_fields = ['ip_address', 'reason']
    readonly_fields = ['created_at', 'auto_generated']
    actions = ['activate', 'deactivate', 'extend_expiry']
    
    def status_icon(self, obj):
        if obj.is_expired():
            return format_html(
                '<span style="color: orange;">⏰ Expired</span>'
            )
        elif obj.is_active:
            return format_html(
                '<span style="color: red;">🚫 Blocked</span>'
            )
        else:
            return format_html(
                '<span style="color: green;">✓ Inactive</span>'
            )
    status_icon.short_description = 'Status'
    
    def activate(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} entries activated.')
    activate.short_description = 'Activate selected entries'
    
    def deactivate(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} entries deactivated.')
    deactivate.short_description = 'Deactivate selected entries'
    
    def extend_expiry(self, request, queryset):
        from datetime import timedelta
        new_expiry = timezone.now() + timedelta(days=7)
        updated = queryset.update(expires_at=new_expiry)
        self.message_user(request, f'{updated} entries extended by 7 days.')
    extend_expiry.short_description = 'Extend expiry by 7 days'


@admin.register(RateLimitRule)
class RateLimitRuleAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'path_pattern', 'method', 'requests_per_minute',
        'requests_per_hour', 'is_active', 'applies_to'
    ]
    list_filter = ['is_active', 'method', 'applies_to_authenticated', 'applies_to_anonymous']
    search_fields = ['name', 'path_pattern']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Rule Information', {
            'fields': ('name', 'path_pattern', 'method', 'is_active')
        }),
        ('Rate Limits', {
            'fields': ('requests_per_minute', 'requests_per_hour', 'requests_per_day')
        }),
        ('Applies To', {
            'fields': ('applies_to_authenticated', 'applies_to_anonymous')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def applies_to(self, obj):
        applies = []
        if obj.applies_to_authenticated:
            applies.append('Authenticated')
        if obj.applies_to_anonymous:
            applies.append('Anonymous')
        return ', '.join(applies) if applies else 'None'
    applies_to.short_description = 'Applies To'


@admin.register(SessionSecurity)
class SessionSecurityAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'ip_address', 'location', 'created_at',
        'last_activity', 'is_active', 'suspicious_icon'
    ]
    list_filter = ['is_active', 'created_at', 'last_activity']
    search_fields = ['user__username', 'user__email', 'ip_address', 'location']
    readonly_fields = ['session_key', 'created_at', 'device_fingerprint']
    date_hierarchy = 'created_at'
    actions = ['deactivate_sessions']
    
    def suspicious_icon(self, obj):
        if obj.is_suspicious():
            return format_html(
                '<span style="color: red;">⚠️ Suspicious</span>'
            )
        else:
            return format_html(
                '<span style="color: green;">✓ Normal</span>'
            )
    suspicious_icon.short_description = 'Status'
    
    def deactivate_sessions(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} sessions deactivated.')
    deactivate_sessions.short_description = 'Deactivate selected sessions'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


# Custom admin views for security dashboard
class SecurityDashboard:
    """Custom admin dashboard for security overview."""
    
    @staticmethod
    def get_security_stats():
        """Get security statistics for dashboard."""
        from datetime import timedelta
        
        now = timezone.now()
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)
        
        stats = {
            'events_24h': SecurityEvent.objects.filter(timestamp__gte=last_24h).count(),
            'events_7d': SecurityEvent.objects.filter(timestamp__gte=last_7d).count(),
            'unresolved_events': SecurityEvent.objects.filter(resolved=False).count(),
            'critical_events': SecurityEvent.objects.filter(
                severity='critical', resolved=False
            ).count(),
            'blocked_ips': IPBlacklist.objects.filter(is_active=True).count(),
            'whitelisted_ips': IPWhitelist.objects.filter(is_active=True).count(),
            'active_sessions': SessionSecurity.objects.filter(is_active=True).count(),
            'suspicious_sessions': SessionSecurity.objects.filter(
                is_active=True
            ).count(),  # This would need custom logic
        }
        
        return stats


# Register custom admin site modifications
from django.contrib.admin import AdminSite
from django.template.response import TemplateResponse

class SecurityAdminSite(AdminSite):
    """Custom admin site with security dashboard."""
    
    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['security_stats'] = SecurityDashboard.get_security_stats()
        return super().index(request, extra_context)


# Add custom CSS for better visualization
class SecurityAdminMixin:
    """Mixin to add custom CSS to security admin pages."""
    
    class Media:
        css = {
            'all': ('admin/css/security_admin.css',)
        }
        js = ('admin/js/security_admin.js',)