from reviews.models import Contributor

Contributor.objects.filter(book__title='The Talisman')
