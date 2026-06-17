from django.urls import path

from . import views

urlpatterns = [
    path("find-tutor/", views.find_tutor, name="find_tutor"),
    path("search-results/", views.search_results, name="search_results"),
]
