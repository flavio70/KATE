from django.contrib import admin
from django.apps import apps
from .models import *

myapp = apps.get_app_config('taws')
for models in myapp.models.values():
	admin.site.register(models)

