from django.apps import AppConfig


class SecurityConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'security'
    verbose_name = 'Security'
    
    def ready(self):
        """Initialize security app when Django starts."""
        # Import signal handlers
        try:
            from . import signals
        except ImportError:
            pass
        
        # Initialize security monitoring
        self.setup_security_monitoring()
    
    def setup_security_monitoring(self):
        """Set up security monitoring and cleanup tasks."""
        from django.core.cache import cache
        from django.utils import timezone
        import logging
        
        logger = logging.getLogger(__name__)
        
        try:
            # Initialize security cache keys
            cache.set('security_app_initialized', True, 3600)
            
            # Log security app initialization
            logger.info("Security app initialized successfully")
            
            # Schedule cleanup tasks (if using celery)
            self.schedule_cleanup_tasks()
            
        except Exception as e:
            logger.error(f"Failed to initialize security monitoring: {e}")
    
    def schedule_cleanup_tasks(self):
        """Schedule periodic cleanup tasks for security data."""
        try:
            # Try to import celery for task scheduling
            from celery import current_app
            
            # Schedule daily cleanup of expired entries
            current_app.conf.beat_schedule.update({
                'cleanup-expired-blacklist': {
                    'task': 'security.tasks.cleanup_expired_blacklist',
                    'schedule': 3600.0,  # Every hour
                },
                'cleanup-old-security-events': {
                    'task': 'security.tasks.cleanup_old_security_events',
                    'schedule': 86400.0,  # Daily
                },
                'cleanup-old-audit-logs': {
                    'task': 'security.tasks.cleanup_old_audit_logs',
                    'schedule': 86400.0,  # Daily
                },
                'detect-suspicious-patterns': {
                    'task': 'security.tasks.detect_suspicious_patterns',
                    'schedule': 1800.0,  # Every 30 minutes
                },
            })
            
        except ImportError:
            # Celery not available, skip task scheduling
            pass
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Could not schedule security cleanup tasks: {e}")