from django.urls import path
from . import views

urlpatterns = [
    path("fetch/", views.fetch_raw_data, name="fetch_raw_data"),
    path("normalize/", views.normalize_data, name="normalize_data"),
    path("submit/", views.submit_cleaned_data, name="submit_cleaned_data"),
]
