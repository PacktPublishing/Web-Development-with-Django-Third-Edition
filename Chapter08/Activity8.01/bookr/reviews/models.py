from django.contrib import auth
from django.db import models


class Publisher(models.Model):
    """A company that publishes books."""
    name = models.CharField(max_length=50,
                            help_text="The name of the Publisher.")
    website = models.URLField(help_text="The Publisher's website.")
    email = models.EmailField(blank=True,
                              help_text="The Publisher's email address.")

    def __str__(self):
        return self.name


class Book(models.Model):
    """A published book."""
    title = models.CharField(max_length=70,
                             help_text="The title of the book.")
    publication_date = models.DateField(
        verbose_name="Date the book was published.")
    isbn = models.CharField(blank=True, max_length=20,
                            verbose_name="ISBN number of the book.")
    publisher = models.ForeignKey(Publisher,
                                  on_delete=models.CASCADE)
    contributors = models.ManyToManyField('Contributor',
                                          through="BookContributor")
    cover = models.ImageField(null=True, blank=True, upload_to="book_covers/")
    sample = models.FileField(null=True, blank=True, upload_to="book_samples/")

    def __str__(self):
        return f"{self.title} ({self.isbn})"


class Contributor(models.Model):
    """A contributor to a Book, e.g. author, editor, co-author."""
    first_names = models.CharField(max_length=50,
                                   help_text="The contributor's first name or names.")
    last_names = models.CharField(blank=True, max_length=50,
                                  help_text="The contributor's last name or names.")
    email = models.EmailField(blank=True,
                              help_text="The contact email for the contributor.")


class BookContributor(models.Model):
    class ContributionRole(models.TextChoices):
        AUTHOR = "AUTHOR", "Author"
        CO_AUTHOR = "CO_AUTHOR", "Co-Author"
        EDITOR = "EDITOR", "Editor"

    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    contributor = models.ForeignKey(Contributor, on_delete=models.CASCADE)
    role = models.CharField(verbose_name="The role this contributor had in the book.",
                            choices=ContributionRole.choices, max_length=20)

    def initialled_name(self):
        """ 
        self.first_names='Jerome David', self.last_names='Salinger' => 'Salinger, JD'
        self.first_names='Plato', self.last_names='' => 'Plato'
        """
        initials = ''.join([name[0] for name
                            in self.first_names.split(' ')])
        return f"{self.last_names}, {initials}"

    def __str__(self):
        return self.initialled_name()


class Review(models.Model):
    content = models.TextField(help_text="The Review text.")
    rating = models.IntegerField(help_text="The rating the reviewer has given.")
    date_created = models.DateTimeField(auto_now_add=True,
                                        help_text="The date and time the review was created.")
    date_edited = models.DateTimeField(null=True,
                                       help_text="The date and time the review was last edited.")
    creator = models.ForeignKey(auth.get_user_model(), on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE,
                             help_text="The Book that this review is for.")
