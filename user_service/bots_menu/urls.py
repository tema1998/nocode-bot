from django.urls import path

from .views import (
    BotMainMenuButtonView,
    BotMainMenuView,
    CreateBotMainMenuButtonView,
    DeleteBotMainMenuButtonView,
    UpdateBotMainMenuButtonView,
)


urlpatterns = [
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
    path(
        "create-main-menu-button/<int:bot_id>",
        CreateBotMainMenuButtonView.as_view(),
        name="create-bot-main-menu-button",
    ),
    path(
        "delete-main-menu-button/<int:bot_id>/<int:button_id>",
        DeleteBotMainMenuButtonView.as_view(),
        name="delete-bot-main-menu-button",
    ),
]
