from django import template

register = template.Library()


@register.simple_tag
def list_items(iterable, *fields):
    return ', '.join([' '.join([getattr(item, field, '') for field in fields]) 
    		          for item in iterable])
