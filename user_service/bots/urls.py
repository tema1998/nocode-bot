from django.urls import path

from .views import AddBotView, BotDefaultReplyView, BotDetailView, BotsView


urlpatterns = [
    path("", BotsView.as_view(), name="bots"),
    path("add-bot", AddBotView.as_view(), name="add-bot"),
    path("<int:bot_id>", BotDetailView.as_view(), name="bot-details"),
    path(
        "default-reply/<int:bot_id>",
        BotDefaultReplyView.as_view(),
        name="bot-default-reply",
    ),
]
