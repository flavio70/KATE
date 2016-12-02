from django import template
from django.template.defaultfilters import stringfilter
from django.contrib.auth.models import Group

register = template.Library()

"""
In order to use these custom filters
use the following tag 
{% load kate_extra %}
into your template

"""

@register.filter
@stringfilter
def lower(value):
	"""Converts a string into all lowercase"""
	return value.lower()

@register.filter
@stringfilter
def replace(value, arg1, arg2):
	"""replace all values of arg1 with arg2"""
	return value.replace(arg1, arg2)

@register.filter
def divide(value, arg): 
	return round((float(value) / float(arg))*100) if float(arg)!=0 else 0

@register.filter
def sub(value, arg): 
	return round(float(value) - float(arg))

@register.filter
def evaluate_color(value): 
	if float(value) > 98: return "success"
	if float(value) > 95: return "warning"
	return "danger"

@register.filter(name='has_group')
def has_group(user, group_name):
	group = Group.objects.get(name=group_name)
	return True if group in user.groups.all() else False


