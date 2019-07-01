"""Settings file that overrides values from settings.py with values needed during unit tests."""

from .settings import *

DEBUG = False

# in case SECRET_KEY is not set in the testing machine's environment
SECRET_KEY = 'secret'

ALLOWED_HOSTS = []

# Revert security settings that are recommended for production but unneeded for testing
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
SECURE_CONTENT_TYPE_NOSNIFF = False
SECURE_BROWSER_XSS_FILTER = False
SECURE_SSL_REDIRECT = False

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

LOGGING = {}

# revert STATICFILES_STORAGE to the default
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
