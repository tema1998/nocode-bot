from django.urls import path

from .views import AddBotView


urlpatterns = [
    path("add-bot", AddBotView.as_view(), name="add-bot"),
]
