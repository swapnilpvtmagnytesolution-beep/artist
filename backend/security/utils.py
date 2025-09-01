import hashlib
import secrets
import string
from datetime import datetime, timedelta
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import re
import logging

logger = logging.getLogger(__name__)


class SecurityUtils:
    """Utility class for security-related operations."""
    
    @staticmethod
    def generate_secure_token(length=32):
        """Generate a cryptographically secure random token."""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    @staticmethod
    def generate_event_id(length=8):
        """Generate a unique event ID."""
        # Use uppercase letters and numbers for better readability
        alphabet = string.ascii_uppercase + string.digits
        # Exclude confusing characters
        alphabet = alphabet.replace('0', '').replace('O', '').replace('1', '').replace('I')
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    @staticmethod
    def hash_password(password, salt=None):
        """Hash a password with salt."""
        if salt is None:
            salt = secrets.token_hex(16)
        
        # Use PBKDF2 with SHA256
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt.encode(),
            iterations=100000,
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return f"{salt}:{key.decode()}"
    
    @staticmethod
    def verify_password(password, hashed_password):
        """Verify a password against its hash."""
        try:
            salt, key = hashed_password.split(':')
            return SecurityUtils.hash_password(password, salt) == hashed_password
        except ValueError:
            return False
    
    @staticmethod
    def encrypt_data(data, key=None):
        """Encrypt sensitive data."""
        if key is None:
            key = settings.SECRET_KEY.encode()
        
        # Derive a key from the secret key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'eddits_salt',  # In production, use a random salt
            iterations=100000,
        )
        
        derived_key = base64.urlsafe_b64encode(kdf.derive(key))
        fernet = Fernet(derived_key)
        
        encrypted_data = fernet.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()
    
    @staticmethod
    def decrypt_data(encrypted_data, key=None):
        """Decrypt sensitive data."""
        try:
            if key is None:
                key = settings.SECRET_KEY.encode()
            
            # Derive the same key
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'eddits_salt',
                iterations=100000,
            )
            
            derived_key = base64.urlsafe_b64encode(kdf.derive(key))
            fernet = Fernet(derived_key)
            
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = fernet.decrypt(encrypted_bytes)
            return decrypted_data.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return None
    
    @staticmethod
    def generate_csrf_token():
        """Generate a CSRF token."""
        return hashlib.sha256(
            f"{secrets.token_hex(16)}{timezone.now().isoformat()}".encode()
        ).hexdigest()
    
    @staticmethod
    def validate_password_strength(password):
        """Validate password strength."""
        errors = []
        
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        
        if not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if not re.search(r'\d', password):
            errors.append("Password must contain at least one digit")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character")
        
        # Check for common passwords
        common_passwords = [
            'password', '123456', 'password123', 'admin', 'qwerty',
            'letmein', 'welcome', 'monkey', '1234567890'
        ]
        
        if password.lower() in common_passwords:
            errors.append("Password is too common")
        
        return errors
    
    @staticmethod
    def sanitize_filename(filename):
        """Sanitize filename to prevent directory traversal."""
        # Remove path separators and dangerous characters
        filename = re.sub(r'[/\\:*?"<>|]', '_', filename)
        
        # Remove leading dots and spaces
        filename = filename.lstrip('. ')
        
        # Limit length
        if len(filename) > 255:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            filename = name[:255-len(ext)-1] + '.' + ext if ext else name[:255]
        
        return filename
    
    @staticmethod
    def validate_file_type(file, allowed_types):
        """Validate file type based on content, not just extension."""
        import magic
        
        try:
            # Get MIME type from file content
            mime_type = magic.from_buffer(file.read(1024), mime=True)
            file.seek(0)  # Reset file pointer
            
            return mime_type in allowed_types
        except Exception as e:
            logger.error(f"File type validation failed: {e}")
            return False
    
    @staticmethod
    def check_file_size(file, max_size_mb=50):
        """Check if file size is within limits."""
        max_size_bytes = max_size_mb * 1024 * 1024
        
        if hasattr(file, 'size'):
            return file.size <= max_size_bytes
        
        # For file-like objects
        file.seek(0, 2)  # Seek to end
        size = file.tell()
        file.seek(0)  # Reset to beginning
        
        return size <= max_size_bytes
    
    @staticmethod
    def generate_access_token(event_id, client_email, expires_in_hours=24):
        """Generate a temporary access token for event access."""
        expiry = timezone.now() + timedelta(hours=expires_in_hours)
        
        token_data = {
            'event_id': event_id,
            'client_email': client_email,
            'expires_at': expiry.isoformat(),
            'token': secrets.token_urlsafe(32)
        }
        
        # Store in cache
        cache_key = f"access_token:{token_data['token']}"
        cache.set(cache_key, token_data, expires_in_hours * 3600)
        
        return token_data['token']
    
    @staticmethod
    def validate_access_token(token):
        """Validate and retrieve access token data."""
        cache_key = f"access_token:{token}"
        token_data = cache.get(cache_key)
        
        if not token_data:
            return None
        
        # Check expiry
        expiry = datetime.fromisoformat(token_data['expires_at'])
        if timezone.now() > expiry.replace(tzinfo=timezone.utc):
            cache.delete(cache_key)
            return None
        
        return token_data
    
    @staticmethod
    def log_security_event(event_type, details, request=None):
        """Log security events for monitoring."""
        log_data = {
            'event_type': event_type,
            'details': details,
            'timestamp': timezone.now().isoformat(),
        }
        
        if request:
            log_data.update({
                'ip_address': SecurityUtils.get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'user': str(request.user) if hasattr(request, 'user') and request.user.is_authenticated else 'Anonymous',
                'path': request.path,
                'method': request.method,
            })
        
        logger.warning(f"Security Event: {log_data}")
        
        # Store in cache for monitoring dashboard
        cache_key = f"security_events:{timezone.now().strftime('%Y-%m-%d')}"
        events = cache.get(cache_key, [])
        events.append(log_data)
        
        # Keep only last 1000 events per day
        if len(events) > 1000:
            events = events[-1000:]
        
        cache.set(cache_key, events, 86400)  # 24 hours
    
    @staticmethod
    def get_client_ip(request):
        """Get the real client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @staticmethod
    def is_suspicious_activity(request):
        """Detect suspicious activity patterns."""
        client_ip = SecurityUtils.get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Check for common bot patterns
        bot_patterns = [
            r'bot', r'crawler', r'spider', r'scraper',
            r'curl', r'wget', r'python-requests'
        ]
        
        for pattern in bot_patterns:
            if re.search(pattern, user_agent, re.IGNORECASE):
                return True, f"Bot-like user agent: {user_agent}"
        
        # Check for rapid requests from same IP
        cache_key = f"request_count:{client_ip}"
        request_count = cache.get(cache_key, 0)
        
        if request_count > 100:  # More than 100 requests per minute
            return True, f"High request rate from IP: {client_ip}"
        
        cache.set(cache_key, request_count + 1, 60)  # 1 minute window
        
        # Check for suspicious paths
        suspicious_paths = [
            '/admin/', '/.env', '/wp-admin/', '/phpmyadmin/',
            '/config/', '/backup/', '/database/'
        ]
        
        for path in suspicious_paths:
            if path in request.path and not request.user.is_staff:
                return True, f"Access to suspicious path: {request.path}"
        
        return False, None
    
    @staticmethod
    def clean_user_input(input_string):
        """Clean and sanitize user input."""
        if not isinstance(input_string, str):
            return input_string
        
        # Remove potentially dangerous characters
        cleaned = re.sub(r'[<>"\'\/\\]', '', input_string)
        
        # Limit length
        cleaned = cleaned[:1000]
        
        # Strip whitespace
        cleaned = cleaned.strip()
        
        return cleaned


# Convenience functions
def generate_secure_token(length=32):
    return SecurityUtils.generate_secure_token(length)

def generate_event_id(length=8):
    return SecurityUtils.generate_event_id(length)

def validate_password_strength(password):
    return SecurityUtils.validate_password_strength(password)

def log_security_event(event_type, details, request=None):
    return SecurityUtils.log_security_event(event_type, details, request)