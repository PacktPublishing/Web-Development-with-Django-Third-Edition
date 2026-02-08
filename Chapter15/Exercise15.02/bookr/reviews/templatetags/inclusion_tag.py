from django import template

register = template.Library()

@register.inclusion_tag('book_list_item.html')
def book_list_item(book):
    return {'item': book}

