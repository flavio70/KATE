from django import template
from django.contrib.auth.models import Group

register = template.Library()

"""
In order to use these custom filters
use the following tag 
{% load kate_group %}
into your template

"""

@register.filter(name='has_group')
def has_group(user, group_name):
	group = Group.objects.get(name=group_name)
	return True if group in user.groups.all() else False

