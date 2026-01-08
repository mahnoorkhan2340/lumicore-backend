from django.urls import path
from . import views

urlpatterns = [
    path("normalize/", views.normalize_data, name="normalize_data"),
]
