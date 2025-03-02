from django.urls import path

from .views import AddBotView, BotsView


urlpatterns = [
    path("", BotsView.as_view(), name="bots"),
    path("add-bot", AddBotView.as_view(), name="add-bot"),
]
