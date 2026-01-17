from django.contrib import admin
from django.utils.html import format_html

from reviews.models import (Publisher, Contributor,
                            Book, BookContributor, Review, ReviewerProfile)


class BookAdmin(admin.ModelAdmin):
    date_hierarchy = "publication_date"
    list_display = ("title", "isbn13")
    list_filter = ("publisher", "publication_date")
    search_fields = ('title', 'isbn', 'publisher__name')

    @admin.display(
        ordering='isbn',
        description='ISBN-13',
        empty_value='-/-'
    )
    def isbn13(self, obj):
        """ '9780316769174' => '978-0-31-676917-4'
         '0316769174' => '0316769174'
         None => '' """
        if obj.isbn:
            if len(obj.isbn)==13:
                return "-".join([obj.isbn[0:3],
                    obj.isbn[3:4], obj.isbn[4:6],
                    obj.isbn[6:12], obj.isbn[12:13]])
            return obj.isbn
        return ""


class ContributorAdmin(admin.ModelAdmin):
    list_display = ('last_names', 'first_names')
    list_filter = ('last_names',)
    search_fields = ('last_names__startswith', 'first_names')


class ReviewAdmin(admin.ModelAdmin):
    fieldsets = (('Linkage', {'fields': ('creator', 'book')}),
                 ('Review content',
                  {'fields': ('content', 'rating')}))
    list_display = ('book__title', 'creator__username', 'rating')


class ReviewerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'has_profile_photo')
    list_editable= ('location',)

    def has_profile_photo(self, obj):
        return obj.profile_photo and format_html('<h1>&#128444; </h1>') or ''


admin.site.register(Publisher)
admin.site.register(Contributor, ContributorAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(BookContributor)
admin.site.register(Review, ReviewAdmin)
admin.site.register(ReviewerProfile, ReviewerProfileAdmin)
