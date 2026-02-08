import urllib.parse

from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def link_worldcat(value, identifier):
    """
    >>> link_worldcat(None, '')
    'https://www.worldcat.org/search?q=The+Iliad'
    >>> link_worldcat('The Iliad', 'title')
    'https://www.worldcat.org/search?q=The+Iliad'
    >>> link_worldcat('9781727518603', 'isbn')
    'https://www.worldcat.org/isbn/9781727518603'
    """
    if not value:
        return ""
    elif identifier=='title':
        link = urllib.parse.quote_plus(value)
        return f"https://www.worldcat.org/search?q={link}"
    else:
        return f"https://www.worldcat.org/isbn/{value}"
