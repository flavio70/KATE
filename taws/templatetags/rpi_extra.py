from django import template
from django.contrib.auth.models import Group
from django.conf import settings

register = template.Library()

"""
In order to use these custom filters
use the following tag 
{% load kate_group %}
into your template

"""

@register.filter(name='has_app')
def has_app(app_name):
	return True if app_name in settings.INSTALLED_APPS else False

