import os
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-default-key-for-development-only')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'storages',
    'drf_yasg',  # Swagger/OpenAPI
    
    # Local apps
    'users',
    'events',
    'dashboard',
    'queries',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # For static files in production
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # CORS headers
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # For multi-language support
]

ROOT_URLCONF = 'eddits_portal.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'eddits_portal.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# Default to PostgreSQL, but can be switched to MySQL by changing environment variables
DATABASE_ENGINE = os.getenv('DATABASE_ENGINE', 'django.db.backends.postgresql')

DATABASES = {
    'default': {
        'ENGINE': DATABASE_ENGINE,
        'NAME': os.getenv('DATABASE_NAME', 'eddits_db'),
        'USER': os.getenv('DATABASE_USER', 'postgres'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD', 'postgres'),
        'HOST': os.getenv('DATABASE_HOST', 'localhost'),
        'PORT': os.getenv('DATABASE_PORT', '5432'),
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Available languages for the application
from django.utils.translation import gettext_lazy as _
LANGUAGES = [
    ('en', _('English')),
    ('hi', _('Hindi')),
    # Add more languages as needed
]

LOCALE_PATHS = [os.path.join(BASE_DIR, 'locale')]

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Media files (Uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',  # For browsable API
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
}

# JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# CORS settings
CORS_ALLOW_ALL_ORIGINS = DEBUG  # Allow all origins in development
CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:3000,http://localhost:19006').split(',')
CORS_ALLOW_CREDENTIALS = True

# Email settings
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST', '')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@eddits.com')

# Storage settings (AWS S3, Google Cloud Storage, or local)
STORAGE_TYPE = os.getenv('STORAGE_TYPE', 'local')  # 'local', 's3', 'gcs', 'do'

if STORAGE_TYPE == 's3':
    # AWS S3 settings
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME', 'us-east-1')
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
    }
    AWS_DEFAULT_ACL = 'private'
    AWS_QUERYSTRING_AUTH = True
    AWS_QUERYSTRING_EXPIRE = 3600  # URL expiration time in seconds
    
    # S3 static settings
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    
    # S3 media settings
    DEFAULT_FILE_STORAGE = 'eddits_portal.storage_backends.MediaStorage'

elif STORAGE_TYPE == 'gcs':
    # Google Cloud Storage settings
    GS_BUCKET_NAME = os.getenv('GS_BUCKET_NAME')
    GS_PROJECT_ID = os.getenv('GS_PROJECT_ID')
    GS_CREDENTIALS = os.getenv('GS_CREDENTIALS')
    GS_DEFAULT_ACL = 'private'
    GS_QUERYSTRING_AUTH = True
    GS_EXPIRATION = timedelta(hours=1)
    
    # GCS static settings
    STATICFILES_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
    
    # GCS media settings
    DEFAULT_FILE_STORAGE = 'eddits_portal.storage_backends.MediaStorage'

elif STORAGE_TYPE == 'do':
    # DigitalOcean Spaces settings
    AWS_ACCESS_KEY_ID = os.getenv('DO_SPACES_ACCESS_KEY')
    AWS_SECRET_ACCESS_KEY = os.getenv('DO_SPACES_SECRET_KEY')
    AWS_STORAGE_BUCKET_NAME = os.getenv('DO_SPACES_BUCKET_NAME')
    AWS_S3_REGION_NAME = os.getenv('DO_SPACES_REGION_NAME', 'nyc3')
    AWS_S3_ENDPOINT_URL = f'https://{AWS_S3_REGION_NAME}.digitaloceanspaces.com'
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.{AWS_S3_REGION_NAME}.digitaloceanspaces.com'
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
    }
    AWS_DEFAULT_ACL = 'private'
    AWS_QUERYSTRING_AUTH = True
    AWS_QUERYSTRING_EXPIRE = 3600  # URL expiration time in seconds
    
    # DO Spaces static settings
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    
    # DO Spaces media settings
    DEFAULT_FILE_STORAGE = 'eddits_portal.storage_backends.MediaStorage'

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'eddits_portal.log'),
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Ensure logs directory exists
os.makedirs(os.path.join(BASE_DIR, 'logs'), exist_ok=True)

# Custom settings for Eddits Portal
EDDITS_PORTAL = {
    'APP_NAME': 'Eddits By Meet Dudhwala',
    'ADMIN_EMAIL': os.getenv('ADMIN_EMAIL', 'admin@eddits.com'),
    'DEFAULT_ALBUM_EXPIRY_DAYS': 90,  # Default expiry for albums in days
    'ENABLE_WATERMARK': os.getenv('ENABLE_WATERMARK', 'False') == 'True',
    'WATERMARK_TEXT': os.getenv('WATERMARK_TEXT', 'Eddits By Meet Dudhwala'),
    'WATERMARK_OPACITY': float(os.getenv('WATERMARK_OPACITY', 0.3)),
    'ENABLE_AI_TAGGING': os.getenv('ENABLE_AI_TAGGING', 'False') == 'True',
}