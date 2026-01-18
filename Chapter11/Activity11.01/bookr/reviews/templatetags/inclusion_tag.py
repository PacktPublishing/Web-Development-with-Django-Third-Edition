from django import template

from ..models import Review

register = template.Library()

@register.inclusion_tag('book_list_item.html')
def book_list_item(book):
    return {'item': book}


@register.inclusion_tag('review_list.html')
def review_list(username):
  """Render the list of reviews written by a user.
  :param: str username The username for whom the books should be fetched
  :return: dict of books read by user
  """
  reviews = Review.objects.filter(creator__username__contains=username)
  return {'review_list': [(review.id, review.book.title) for review in reviews]}

