from django.urls import include, path

from .views import (
    AddBotView,
    BotDefaultReplyView,
    BotDeleteView,
    BotDetailView,
    BotsView,
    BotUsersView,
)


urlpatterns = [
    path("", BotsView.as_view(), name="bots"),
    path("add/", AddBotView.as_view(), name="add-bot"),
    path(
        "<int:bot_id>/",
        include(
            [
                path("", BotDetailView.as_view(), name="bot-detail"),
                path("delete/", BotDeleteView.as_view(), name="bot-delete"),
                path(
                    "default-reply/",
                    BotDefaultReplyView.as_view(),
                    name="bot-default-reply",
                ),
                path("users/", BotUsersView.as_view(), name="bot-users"),
            ]
        ),
    ),
]
