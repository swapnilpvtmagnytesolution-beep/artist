"""WSGI config for eddits_backend project in production."""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eddits_backend.settings_prod')

application = get_wsgi_application()