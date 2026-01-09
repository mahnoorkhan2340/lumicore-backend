from django.urls import path
from . import views

urlpatterns = [
    path('data/', views.fetch_raw_data),
    path('normalize/', views.normalize_data),
    path('submit/', views.submit_cleaned_data),
]
