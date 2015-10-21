from django import template

register=template.Library()

@register.filter
def culo(aaa):
	return aaa.lower()
