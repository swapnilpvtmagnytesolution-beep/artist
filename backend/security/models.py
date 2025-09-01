from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import validate_ipv4_address, validate_ipv6_address
from django.core.exceptions import ValidationError

User = get_user_model()


def validate_ip_address(value):
    """Validate IPv4 or IPv6 address."""
    try:
        validate_ipv4_address(value)
    except ValidationError:
        try:
            validate_ipv6_address(value)
        except ValidationError:
            raise ValidationError('Enter a valid IPv4 or IPv6 address.')


class SecurityEvent(models.Model):
    """Model to track security events and suspicious activities."""
    
    EVENT_TYPES = [
        ('login_attempt', 'Login Attempt'),
        ('login_success', 'Login Success'),
        ('login_failure', 'Login Failure'),
        ('password_change', 'Password Change'),
        ('permission_denied', 'Permission Denied'),
        ('suspicious_activity', 'Suspicious Activity'),
        ('rate_limit_exceeded', 'Rate Limit Exceeded'),
        ('file_upload', 'File Upload'),
        ('file_download', 'File Download'),
        ('data_access', 'Data Access'),
        ('admin_action', 'Admin Action'),
        ('api_access', 'API Access'),
        ('csrf_failure', 'CSRF Failure'),
        ('ip_blocked', 'IP Blocked'),
        ('account_locked', 'Account Locked'),
    ]
    
    SEVERITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS, default='medium')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField(validators=[validate_ip_address])
    user_agent = models.TextField(blank=True)
    path = models.CharField(max_length=500, blank=True)
    method = models.CharField(max_length=10, blank=True)
    details = models.JSONField(default=dict)
    timestamp = models.DateTimeField(default=timezone.now)
    resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='resolved_security_events'
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['event_type', 'timestamp']),
            models.Index(fields=['ip_address', 'timestamp']),
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['severity', 'resolved']),
        ]
    
    def __str__(self):
        return f"{self.event_type} - {self.ip_address} - {self.timestamp}"
    
    def mark_resolved(self, resolved_by_user, notes=''):
        """Mark the security event as resolved."""
        self.resolved = True
        self.resolved_by = resolved_by_user
        self.resolved_at = timezone.now()
        self.notes = notes
        self.save()


class AuditLog(models.Model):
    """Model to track all user actions for audit purposes."""
    
    ACTION_TYPES = [
        ('create', 'Create'),
        ('read', 'Read'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('download', 'Download'),
        ('upload', 'Upload'),
        ('share', 'Share'),
        ('export', 'Export'),
        ('import', 'Import'),
        ('admin', 'Admin Action'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=20, choices=ACTION_TYPES)
    resource_type = models.CharField(max_length=50)  # e.g., 'event', 'photo', 'user'
    resource_id = models.CharField(max_length=100, blank=True)
    resource_name = models.CharField(max_length=200, blank=True)
    ip_address = models.GenericIPAddressField(validators=[validate_ip_address])
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    details = models.JSONField(default=dict)
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
            models.Index(fields=['resource_type', 'timestamp']),
            models.Index(fields=['ip_address', 'timestamp']),
        ]
    
    def __str__(self):
        user_str = str(self.user) if self.user else 'Anonymous'
        return f"{user_str} - {self.action} - {self.resource_type} - {self.timestamp}"


class IPWhitelist(models.Model):
    """Model to manage IP address whitelist."""
    
    ip_address = models.GenericIPAddressField(
        unique=True,
        validators=[validate_ip_address],
        help_text="IP address to whitelist"
    )
    description = models.CharField(max_length=200, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.ip_address} - {self.description}"
    
    def is_expired(self):
        """Check if the whitelist entry has expired."""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    @classmethod
    def is_whitelisted(cls, ip_address):
        """Check if an IP address is whitelisted and active."""
        return cls.objects.filter(
            ip_address=ip_address,
            is_active=True
        ).exclude(
            expires_at__lt=timezone.now()
        ).exists()


class IPBlacklist(models.Model):
    """Model to manage IP address blacklist."""
    
    ip_address = models.GenericIPAddressField(
        unique=True,
        validators=[validate_ip_address],
        help_text="IP address to blacklist"
    )
    reason = models.CharField(max_length=200)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    auto_generated = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.ip_address} - {self.reason}"
    
    def is_expired(self):
        """Check if the blacklist entry has expired."""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    @classmethod
    def is_blacklisted(cls, ip_address):
        """Check if an IP address is blacklisted and active."""
        return cls.objects.filter(
            ip_address=ip_address,
            is_active=True
        ).exclude(
            expires_at__lt=timezone.now()
        ).exists()
    
    @classmethod
    def auto_blacklist(cls, ip_address, reason, duration_hours=24):
        """Automatically blacklist an IP address for a specified duration."""
        expires_at = timezone.now() + timezone.timedelta(hours=duration_hours)
        
        blacklist_entry, created = cls.objects.get_or_create(
            ip_address=ip_address,
            defaults={
                'reason': reason,
                'expires_at': expires_at,
                'auto_generated': True,
                'created_by_id': 1,  # System user
            }
        )
        
        if not created:
            # Update existing entry
            blacklist_entry.reason = reason
            blacklist_entry.expires_at = expires_at
            blacklist_entry.is_active = True
            blacklist_entry.save()
        
        return blacklist_entry


class RateLimitRule(models.Model):
    """Model to define rate limiting rules."""
    
    name = models.CharField(max_length=100, unique=True)
    path_pattern = models.CharField(
        max_length=200,
        help_text="URL pattern to match (supports wildcards)"
    )
    method = models.CharField(
        max_length=10,
        choices=[('GET', 'GET'), ('POST', 'POST'), ('PUT', 'PUT'), 
                ('DELETE', 'DELETE'), ('*', 'All Methods')],
        default='*'
    )
    requests_per_minute = models.PositiveIntegerField(default=60)
    requests_per_hour = models.PositiveIntegerField(default=1000)
    requests_per_day = models.PositiveIntegerField(default=10000)
    is_active = models.BooleanField(default=True)
    applies_to_authenticated = models.BooleanField(default=True)
    applies_to_anonymous = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.path_pattern}"
    
    def matches_request(self, request):
        """Check if this rule applies to the given request."""
        import fnmatch
        
        # Check method
        if self.method != '*' and request.method != self.method:
            return False
        
        # Check path pattern
        if not fnmatch.fnmatch(request.path, self.path_pattern):
            return False
        
        # Check authentication status
        if request.user.is_authenticated and not self.applies_to_authenticated:
            return False
        
        if not request.user.is_authenticated and not self.applies_to_anonymous:
            return False
        
        return True


class SessionSecurity(models.Model):
    """Model to track session security information."""
    
    session_key = models.CharField(max_length=40, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField(validators=[validate_ip_address])
    user_agent = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    last_activity = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    location = models.CharField(max_length=200, blank=True)
    device_fingerprint = models.CharField(max_length=64, blank=True)
    
    class Meta:
        ordering = ['-last_activity']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['session_key']),
        ]
    
    def __str__(self):
        return f"{self.user} - {self.ip_address} - {self.created_at}"
    
    def update_activity(self):
        """Update the last activity timestamp."""
        self.last_activity = timezone.now()
        self.save(update_fields=['last_activity'])
    
    def is_suspicious(self):
        """Check if this session shows suspicious activity."""
        # Check for multiple IPs for same user
        other_sessions = SessionSecurity.objects.filter(
            user=self.user,
            is_active=True
        ).exclude(id=self.id)
        
        different_ips = other_sessions.exclude(ip_address=self.ip_address).exists()
        
        # Check for rapid location changes
        if different_ips and self.location:
            recent_sessions = other_sessions.filter(
                created_at__gte=timezone.now() - timezone.timedelta(hours=1)
            ).exclude(location=self.location)
            
            if recent_sessions.exists():
                return True
        
        return False