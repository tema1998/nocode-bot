from django.urls import path

from .views import AddBotView, BotDetailView, BotsView


urlpatterns = [
    path("", BotsView.as_view(), name="bots"),
    path("add-bot", AddBotView.as_view(), name="add-bot"),
    path("<int:bot_id>", BotDetailView.as_view(), name="bot-details"),
]
