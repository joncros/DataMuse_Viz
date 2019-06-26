"""Settings file that overrides values from settings.py with values needed during unit tests."""

from .settings import *

DEBUG = False

# in case SECRET_KEY is not set in the testing machine's environment
SECRET_KEY = 'secret'

LOGGING = {}

# revert STATICFILES_STORAGE to the default
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
