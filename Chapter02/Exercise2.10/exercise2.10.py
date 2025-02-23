from reviews.models import Book

book = Book.objects.get(title='The Talisman')

book.contributors.all()
