from django.urls import path

from . import views


urlpatterns = [
    path('books/', views.book_list, name='book_list'),
    path('', views.welcome_view, name='welcome_view'),
]

