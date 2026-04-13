# bot/urls.py
from django.urls import path

from .views import webhook

urlpatterns = [
    path("webhook/<str:secret>/", webhook, name="webhook"),
]
