import os
import sys

# Set up the Python path and the Django environment variable	
APP_HOME = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.extend((APP_HOME, os.path.join(APP_HOME, "mgmt")))
os.environ['DJANGO_SETTINGS_MODULE'] = 'mgmt.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
