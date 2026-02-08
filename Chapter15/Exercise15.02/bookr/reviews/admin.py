from django.contrib import admin
from django.utils.html import format_html

from reviews.models import (Publisher, Contributor,
                            Book, BookContributor, Review, ReviewerProfile)


class PublisherAdmin(admin.ModelAdmin):
    list_per_page = 10
    list_max_show_all = 50


class BookAdmin(admin.ModelAdmin):
    date_hierarchy = "publication_date"
    list_display = ("title", "isbn13")
    list_filter = ("publisher", "publication_date")
    search_fields = ('title', 'isbn', 'publisher__name')
    list_per_page = 10
    list_max_show_all = 50

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


class BookContributorAdmin(admin.ModelAdmin):
    list_per_page = 10
    list_max_show_all = 50


class ContributorAdmin(admin.ModelAdmin):
    list_display = ('last_names', 'first_names')
    list_filter = ('last_names',)
    search_fields = ('last_names__startswith', 'first_names')
    list_per_page = 10
    list_max_show_all = 50


class ReviewAdmin(admin.ModelAdmin):
    fieldsets = (('Linkage', {'fields': ('creator', 'book')}),
                 ('Review content',
                  {'fields': ('content', 'rating')}))
    list_filter = ("rating",)
    list_display = ('book__title', 'creator__username', 'rating_stars')
    list_per_page = 10
    list_max_show_all = 50
    search_fields = ('book__title', 'creator__username', 'content')
    show_full_result_count = False

    def rating_stars(self, obj):
        return obj.rating and format_html('&#9734;'*obj.rating) or ''


class ReviewerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'has_profile_photo')
    list_editable= ('location',)
    list_per_page = 10
    list_max_show_all = 50

    def has_profile_photo(self, obj):
        return obj.profile_photo and format_html('<h1>&#128444; </h1>') or ''


admin.site.register(Publisher, PublisherAdmin)
admin.site.register(Contributor, ContributorAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(BookContributor, BookContributorAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(ReviewerProfile, ReviewerProfileAdmin)
