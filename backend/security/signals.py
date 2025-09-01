from django.db.models.signals import post_save, post_delete, pre_save
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.cache import cache
from .models import SecurityEvent, AuditLog, SessionSecurity, IPBlacklist
from .utils import SecurityUtils
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Log successful user login."""
    try:
        ip_address = SecurityUtils.get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Create security event
        SecurityEvent.objects.create(
            event_type='login_success',
            severity='low',
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            path=request.path,
            method=request.method,
            details={
                'username': user.username,
                'login_time': timezone.now().isoformat(),
            }
        )
        
        # Create audit log
        AuditLog.objects.create(
            user=user,
            action='login',
            resource_type='user',
            resource_id=str(user.id),
            resource_name=user.username,
            ip_address=ip_address,
            user_agent=user_agent,
            success=True
        )
        
        # Create or update session security
        if hasattr(request, 'session'):
            session_key = request.session.session_key
            if session_key:
                SessionSecurity.objects.update_or_create(
                    session_key=session_key,
                    defaults={
                        'user': user,
                        'ip_address': ip_address,
                        'user_agent': user_agent,
                        'last_activity': timezone.now(),
                        'is_active': True,
                    }
                )
        
        # Reset failed login attempts for this IP
        cache_key = f"failed_logins:{ip_address}"
        cache.delete(cache_key)
        
        logger.info(f"User {user.username} logged in from {ip_address}")
        
    except Exception as e:
        logger.error(f"Error logging user login: {e}")


@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    """Log failed user login attempts."""
    try:
        ip_address = SecurityUtils.get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        username = credentials.get('username', 'Unknown')
        
        # Track failed login attempts
        cache_key = f"failed_logins:{ip_address}"
        failed_attempts = cache.get(cache_key, 0) + 1
        cache.set(cache_key, failed_attempts, 3600)  # 1 hour
        
        # Determine severity based on failed attempts
        if failed_attempts >= 10:
            severity = 'critical'
            # Auto-blacklist IP after 10 failed attempts
            IPBlacklist.auto_blacklist(
                ip_address=ip_address,
                reason=f"Too many failed login attempts ({failed_attempts})",
                duration_hours=24
            )
        elif failed_attempts >= 5:
            severity = 'high'
        else:
            severity = 'medium'
        
        # Create security event
        SecurityEvent.objects.create(
            event_type='login_failure',
            severity=severity,
            ip_address=ip_address,
            user_agent=user_agent,
            path=request.path,
            method=request.method,
            details={
                'username': username,
                'failed_attempts': failed_attempts,
                'attempt_time': timezone.now().isoformat(),
            }
        )
        
        # Create audit log
        AuditLog.objects.create(
            action='login',
            resource_type='user',
            resource_name=username,
            ip_address=ip_address,
            user_agent=user_agent,
            success=False,
            error_message=f"Failed login attempt #{failed_attempts}"
        )
        
        logger.warning(
            f"Failed login attempt for {username} from {ip_address} "
            f"(attempt #{failed_attempts})"
        )
        
    except Exception as e:
        logger.error(f"Error logging failed login: {e}")


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Log user logout."""
    try:
        if user:
            ip_address = SecurityUtils.get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            # Create audit log
            AuditLog.objects.create(
                user=user,
                action='logout',
                resource_type='user',
                resource_id=str(user.id),
                resource_name=user.username,
                ip_address=ip_address,
                user_agent=user_agent,
                success=True
            )
            
            # Deactivate session security
            if hasattr(request, 'session'):
                session_key = request.session.session_key
                if session_key:
                    SessionSecurity.objects.filter(
                        session_key=session_key
                    ).update(is_active=False)
            
            logger.info(f"User {user.username} logged out from {ip_address}")
            
    except Exception as e:
        logger.error(f"Error logging user logout: {e}")


@receiver(post_save, sender=User)
def log_user_changes(sender, instance, created, **kwargs):
    """Log user creation and modifications."""
    try:
        action = 'create' if created else 'update'
        
        # Create audit log
        AuditLog.objects.create(
            user=instance if not created else None,
            action=action,
            resource_type='user',
            resource_id=str(instance.id),
            resource_name=instance.username,
            ip_address='127.0.0.1',  # System action
            success=True,
            details={
                'email': instance.email,
                'is_active': instance.is_active,
                'is_staff': instance.is_staff,
                'is_superuser': instance.is_superuser,
            }
        )
        
        if created:
            logger.info(f"New user created: {instance.username}")
        else:
            logger.info(f"User updated: {instance.username}")
            
    except Exception as e:
        logger.error(f"Error logging user changes: {e}")


@receiver(post_delete, sender=User)
def log_user_deletion(sender, instance, **kwargs):
    """Log user deletion."""
    try:
        # Create audit log
        AuditLog.objects.create(
            action='delete',
            resource_type='user',
            resource_id=str(instance.id),
            resource_name=instance.username,
            ip_address='127.0.0.1',  # System action
            success=True,
            details={
                'deleted_user_email': instance.email,
                'was_staff': instance.is_staff,
                'was_superuser': instance.is_superuser,
            }
        )
        
        logger.warning(f"User deleted: {instance.username}")
        
    except Exception as e:
        logger.error(f"Error logging user deletion: {e}")


# Signal for tracking model changes in events app
@receiver(post_save)
def log_model_changes(sender, instance, created, **kwargs):
    """Log changes to important models."""
    try:
        # Only log changes for specific models
        monitored_models = ['Event', 'Photo', 'Video', 'Client']
        model_name = sender.__name__
        
        if model_name not in monitored_models:
            return
        
        action = 'create' if created else 'update'
        
        # Try to get the current user from thread local storage
        # This would require middleware to set the user in thread local
        current_user = getattr(instance, '_current_user', None)
        
        # Create audit log
        AuditLog.objects.create(
            user=current_user,
            action=action,
            resource_type=model_name.lower(),
            resource_id=str(instance.pk),
            resource_name=str(instance),
            ip_address='127.0.0.1',  # Default for system actions
            success=True,
            details={
                'model': model_name,
                'created': created,
            }
        )
        
    except Exception as e:
        logger.error(f"Error logging model changes: {e}")


@receiver(post_delete)
def log_model_deletion(sender, instance, **kwargs):
    """Log deletion of important models."""
    try:
        # Only log deletions for specific models
        monitored_models = ['Event', 'Photo', 'Video', 'Client']
        model_name = sender.__name__
        
        if model_name not in monitored_models:
            return
        
        # Try to get the current user from thread local storage
        current_user = getattr(instance, '_current_user', None)
        
        # Create audit log
        AuditLog.objects.create(
            user=current_user,
            action='delete',
            resource_type=model_name.lower(),
            resource_id=str(instance.pk),
            resource_name=str(instance),
            ip_address='127.0.0.1',  # Default for system actions
            success=True,
            details={
                'model': model_name,
                'deleted_object': str(instance),
            }
        )
        
    except Exception as e:
        logger.error(f"Error logging model deletion: {e}")


# Custom signal for security events
from django.dispatch import Signal

security_event_detected = Signal()


@receiver(security_event_detected)
def handle_security_event(sender, event_type, severity, details, request=None, **kwargs):
    """Handle custom security events."""
    try:
        ip_address = '127.0.0.1'
        user_agent = ''
        path = ''
        method = ''
        user = None
        
        if request:
            ip_address = SecurityUtils.get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            path = request.path
            method = request.method
            user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None
        
        # Create security event
        SecurityEvent.objects.create(
            event_type=event_type,
            severity=severity,
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            path=path,
            method=method,
            details=details
        )
        
        # Log the event
        SecurityUtils.log_security_event(event_type, details, request)
        
        # Take automatic actions for critical events
        if severity == 'critical':
            handle_critical_security_event(event_type, ip_address, details)
        
    except Exception as e:
        logger.error(f"Error handling security event: {e}")


def handle_critical_security_event(event_type, ip_address, details):
    """Handle critical security events with automatic responses."""
    try:
        # Auto-blacklist IP for certain critical events
        auto_blacklist_events = [
            'suspicious_activity',
            'rate_limit_exceeded',
            'csrf_failure',
        ]
        
        if event_type in auto_blacklist_events:
            IPBlacklist.auto_blacklist(
                ip_address=ip_address,
                reason=f"Critical security event: {event_type}",
                duration_hours=1  # Short duration for automatic blocks
            )
            
            logger.critical(
                f"IP {ip_address} auto-blacklisted due to critical security event: {event_type}"
            )
        
        # Send alerts for critical events (implement email/slack notifications)
        send_security_alert(event_type, ip_address, details)
        
    except Exception as e:
        logger.error(f"Error handling critical security event: {e}")


def send_security_alert(event_type, ip_address, details):
    """Send security alerts to administrators."""
    try:
        # This would integrate with your notification system
        # For now, just log the alert
        logger.critical(
            f"SECURITY ALERT: {event_type} from {ip_address}. Details: {details}"
        )
        
        # TODO: Implement email/Slack/SMS notifications
        # send_email_alert(event_type, ip_address, details)
        # send_slack_alert(event_type, ip_address, details)
        
    except Exception as e:
        logger.error(f"Error sending security alert: {e}")