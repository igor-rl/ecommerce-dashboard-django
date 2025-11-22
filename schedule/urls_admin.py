# schedule/urls_admin.py
from django.urls import path
from .views_admin import get_available_hours

urlpatterns = [
    path("get-available-hours/", get_available_hours, name="get_available_hours"),
]
