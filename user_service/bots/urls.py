from django.urls import path

from .views import (
    AddBotView,
    BotDefaultReplyView,
    BotDeleteView,
    BotDetailView,
    BotMainMenuButtonView,
    BotMainMenuView,
    BotsView,
    UpdateBotMainMenuButtonView,
)


urlpatterns = [
    path("", BotsView.as_view(), name="bots"),
    path("add-bot", AddBotView.as_view(), name="add-bot"),
    path("<int:bot_id>", BotDetailView.as_view(), name="bot-details"),
    path("delete/<int:bot_id>", BotDeleteView.as_view(), name="bot-delete"),
    path(
        "default-reply/<int:bot_id>",
        BotDefaultReplyView.as_view(),
        name="bot-default-reply",
    ),
    path(
        "main-menu/<int:bot_id>",
        BotMainMenuView.as_view(),
        name="bot-main-menu",
    ),
    path(
        "main-menu-button/<int:bot_id>/<int:button_id>",
        BotMainMenuButtonView.as_view(),
        name="bot-main-menu-button",
    ),
    path(
        "update-main-menu-button/<int:bot_id>/<int:button_id>",
        UpdateBotMainMenuButtonView.as_view(),
        name="update-bot-main-menu-button",
    ),
]
