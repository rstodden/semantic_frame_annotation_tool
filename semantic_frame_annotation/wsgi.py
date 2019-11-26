"""
WSGI config for semantic_frame_annotation project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/
"""

import os, sys

from django.core.wsgi import get_wsgi_application
sys.path.append("/var/www/annotation_tool")
sys.path.append("/var/www/annotation_tool/semantic_frame_annotation")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "semantic_frame_annotation.settings")

application = get_wsgi_application()

#import django.core.handlers.wsgi
#application = django.core.handlers.wsgi.WSGIHandler()
