# bot/urls.py
from django.urls import path

from .views import webhook, landing

urlpatterns = [
    path("", landing, name="landing"),
    path("webhook/<str:secret>/", webhook, name="webhook"),
]
