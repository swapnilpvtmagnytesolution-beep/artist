import time
import hashlib
from django.core.cache import cache
from django.http import JsonResponse
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser
from ipaddress import ip_address, ip_network
import logging

logger = logging.getLogger(__name__)


class SecurityMiddleware(MiddlewareMixin):
    """Custom security middleware for rate limiting and IP filtering."""
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
        
        # Rate limiting settings
        self.rate_limit_requests = getattr(settings, 'RATE_LIMIT_REQUESTS', 100)
        self.rate_limit_window = getattr(settings, 'RATE_LIMIT_WINDOW', 3600)  # 1 hour
        
        # IP filtering settings
        self.blocked_ips = getattr(settings, 'BLOCKED_IPS', [])
        self.allowed_ips = getattr(settings, 'ALLOWED_IPS', [])
        
        # Suspicious activity detection
        self.max_failed_attempts = getattr(settings, 'MAX_FAILED_ATTEMPTS', 5)
        self.lockout_duration = getattr(settings, 'LOCKOUT_DURATION', 900)  # 15 minutes
    
    def process_request(self, request):
        """Process incoming requests for security checks."""
        
        # Get client IP
        client_ip = self.get_client_ip(request)
        
        # Check IP filtering
        if not self.is_ip_allowed(client_ip):
            logger.warning(f"Blocked request from IP: {client_ip}")
            return JsonResponse(
                {'error': 'Access denied from your IP address'},
                status=403
            )
        
        # Check rate limiting
        if not self.check_rate_limit(client_ip, request):
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return JsonResponse(
                {'error': 'Rate limit exceeded. Please try again later.'},
                status=429
            )
        
        # Check for account lockout
        if self.is_account_locked(client_ip):
            logger.warning(f"Account locked for IP: {client_ip}")
            return JsonResponse(
                {'error': 'Account temporarily locked due to suspicious activity'},
                status=423
            )
        
        return None
    
    def process_response(self, request, response):
        """Process responses to track failed attempts."""
        
        # Track failed login attempts
        if (request.path.endswith('/login/') or 
            request.path.endswith('/event-login/')) and response.status_code == 401:
            
            client_ip = self.get_client_ip(request)
            self.track_failed_attempt(client_ip)
        
        # Reset failed attempts on successful login
        elif (request.path.endswith('/login/') or 
              request.path.endswith('/event-login/')) and response.status_code == 200:
            
            client_ip = self.get_client_ip(request)
            self.reset_failed_attempts(client_ip)
        
        return response
    
    def get_client_ip(self, request):
        """Get the real client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def is_ip_allowed(self, client_ip):
        """Check if IP is allowed based on whitelist/blacklist."""
        
        # Check if IP is explicitly blocked
        if self.blocked_ips:
            for blocked_ip in self.blocked_ips:
                try:
                    if ip_address(client_ip) in ip_network(blocked_ip, strict=False):
                        return False
                except ValueError:
                    continue
        
        # Check if IP is in allowed list (if whitelist is configured)
        if self.allowed_ips:
            for allowed_ip in self.allowed_ips:
                try:
                    if ip_address(client_ip) in ip_network(allowed_ip, strict=False):
                        return True
                except ValueError:
                    continue
            return False  # Not in whitelist
        
        return True  # No restrictions or IP is allowed
    
    def check_rate_limit(self, client_ip, request):
        """Check if request is within rate limits."""
        
        # Skip rate limiting for admin users
        if hasattr(request, 'user') and request.user.is_authenticated and request.user.is_staff:
            return True
        
        # Create cache key
        cache_key = f"rate_limit:{client_ip}"
        
        # Get current request count
        current_requests = cache.get(cache_key, 0)
        
        # Check if limit exceeded
        if current_requests >= self.rate_limit_requests:
            return False
        
        # Increment counter
        cache.set(cache_key, current_requests + 1, self.rate_limit_window)
        
        return True
    
    def track_failed_attempt(self, client_ip):
        """Track failed login attempts."""
        cache_key = f"failed_attempts:{client_ip}"
        
        current_attempts = cache.get(cache_key, 0)
        new_attempts = current_attempts + 1
        
        # Set cache with lockout duration if max attempts reached
        if new_attempts >= self.max_failed_attempts:
            cache.set(f"locked:{client_ip}", True, self.lockout_duration)
            logger.warning(f"IP {client_ip} locked due to {new_attempts} failed attempts")
        
        cache.set(cache_key, new_attempts, self.lockout_duration)
    
    def reset_failed_attempts(self, client_ip):
        """Reset failed attempts counter on successful login."""
        cache.delete(f"failed_attempts:{client_ip}")
        cache.delete(f"locked:{client_ip}")
    
    def is_account_locked(self, client_ip):
        """Check if account is locked."""
        return cache.get(f"locked:{client_ip}", False)


class EventAccessMiddleware(MiddlewareMixin):
    """Middleware to handle event access control and session management."""
    
    def process_request(self, request):
        """Check event access permissions."""
        
        # Skip for admin and auth endpoints
        if (request.path.startswith('/admin/') or 
            request.path.startswith('/api/auth/') or
            request.path.startswith('/api/dashboard/')):
            return None
        
        # Check for event-specific endpoints
        if self.is_event_endpoint(request.path):
            return self.check_event_access(request)
        
        return None
    
    def is_event_endpoint(self, path):
        """Check if the path is an event-specific endpoint."""
        event_endpoints = [
            '/api/photos/by_event/',
            '/api/videos/by_event/',
            '/api/reels/by_event/',
            '/api/events/',
        ]
        
        for endpoint in event_endpoints:
            if endpoint in path:
                return True
        
        return False
    
    def check_event_access(self, request):
        """Check if user has access to the requested event."""
        
        # Get event ID from request
        event_id = self.extract_event_id(request)
        
        if not event_id:
            return None  # No event ID, let the view handle it
        
        # Check if user is authenticated admin
        if hasattr(request, 'user') and request.user.is_authenticated and request.user.is_staff:
            return None  # Admin has access to everything
        
        # Check session for event access
        session_key = f"event_access:{event_id}"
        
        if not request.session.get(session_key, False):
            return JsonResponse(
                {'error': 'Access denied. Please authenticate for this event.'},
                status=403
            )
        
        return None
    
    def extract_event_id(self, request):
        """Extract event ID from request parameters."""
        
        # Try to get from query parameters
        event_id = request.GET.get('event_id')
        if event_id:
            return event_id
        
        # Try to get from POST data
        if hasattr(request, 'data') and isinstance(request.data, dict):
            event_id = request.data.get('event_id')
            if event_id:
                return event_id
        
        # Try to get from URL path
        path_parts = request.path.strip('/').split('/')
        if 'events' in path_parts:
            try:
                event_index = path_parts.index('events')
                if event_index + 1 < len(path_parts):
                    return path_parts[event_index + 1]
            except (ValueError, IndexError):
                pass
        
        return None


class AuditLogMiddleware(MiddlewareMixin):
    """Middleware to log important security events."""
    
    def process_request(self, request):
        """Log security-relevant requests."""
        
        # Log admin access
        if request.path.startswith('/admin/'):
            client_ip = self.get_client_ip(request)
            user = getattr(request, 'user', None)
            
            if user and user.is_authenticated:
                logger.info(f"Admin access: {user.email} from {client_ip} to {request.path}")
            else:
                logger.warning(f"Unauthenticated admin access attempt from {client_ip}")
        
        # Log API access to sensitive endpoints
        sensitive_endpoints = [
            '/api/dashboard/',
            '/api/auth/users/',
            '/api/events/',
        ]
        
        for endpoint in sensitive_endpoints:
            if request.path.startswith(endpoint):
                client_ip = self.get_client_ip(request)
                user = getattr(request, 'user', None)
                
                if user and user.is_authenticated:
                    logger.info(f"API access: {user.email} from {client_ip} to {request.path}")
                else:
                    logger.info(f"Anonymous API access from {client_ip} to {request.path}")
                break
        
        return None
    
    def get_client_ip(self, request):
        """Get the real client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class ContentSecurityMiddleware(MiddlewareMixin):
    """Middleware to add security headers."""
    
    def process_response(self, request, response):
        """Add security headers to response."""
        
        # Content Security Policy
        if not settings.DEBUG:
            response['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' https:; "
                "connect-src 'self' https:; "
                "media-src 'self' https:;"
            )
        
        # Additional security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Remove server information
        if 'Server' in response:
            del response['Server']
        
        return response