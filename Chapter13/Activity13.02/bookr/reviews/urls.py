from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views, api_views

router = DefaultRouter()
router.register(r'books', api_views.BookViewSet)
router.register(r'reviews', api_views.ReviewViewSet)

urlpatterns = [
    path('api/', include((router.urls, 'api'))),
    path('books/', views.book_list, name='book_list'),
    path('books/<int:pk>/', views.book_detail, name='book_detail'),
    path('books/<int:pk>/media/', views.book_media, name='book_media'),
    path('books/<int:pk>/pdf/', views.book_detail_pdf, name='book_detail_pdf'),
    path('books/<int:book_pk>/reviews/new/', views.review_edit, name='review_create'),
    path('books/<int:book_pk>/reviews/<int:review_pk>/',
         views.review_edit, name='review_edit',
    ),
    path('publishers/<int:pk>/', views.publisher_edit, name='publisher_edit'),
    path('publishers/new/', views.publisher_edit, name='publisher_create'),
    path('reviews/csv/', views.review_summary_csv, name='review_summary_csv'),
    path('reviews/profile/<int:user_id>/background_jpg/',
         views.reviewer_profile_jpg, name='reviewer_profile_jpg'),
    path('reviews/profile/<int:user_id>/background_png/',
         views.reviewer_profile_png, name='reviewer_profile_png'),
    path('reviews/statistics/<int:min_publication_year>/<int:max_publication_year>',
         views.review_statistics, name='review_statistics'),
    path('reviews/xlsx/', views.review_summary_xlsx, name='review_summary_xlsx'),
]
