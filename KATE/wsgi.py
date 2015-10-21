"""
WSGI config for KATE project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os,sys

sys.path.append(os.path.abspath("/tools/smotools/www"))
sys.path.append(os.path.abspath("/tools/smotools/www/KATE"))
sys.path.append(os.path.abspath("/tools/smotools/www/KATE/KATE"))

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "KATE.settings")

application = get_wsgi_application()
