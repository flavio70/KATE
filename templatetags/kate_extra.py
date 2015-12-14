from django import template
from django.template.defaultfilters import stringfilter

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
