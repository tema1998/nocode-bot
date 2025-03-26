from django.urls import path

from .views import (
    AddBotView,
    BotChainDetailView,
    BotChainView,
    BotDefaultReplyView,
    BotDeleteView,
    BotDetailView,
    BotMainMenuButtonView,
    BotMainMenuView,
    BotsView,
    CreateBotMainMenuButtonView,
    CreateChainStepView,
    CreateChainView,
    DeleteBotMainMenuButtonView,
    DeleteChainStepView,
    DeleteChainView,
    UpdateBotMainMenuButtonView,
    UpdateChainStepView,
    UpdateChainView,
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
    path(
        "chains/<int:bot_id>/",
        BotChainView.as_view(),
        name="bot-chains",
    ),
    path(
        "chain/<int:bot_id>/<int:chain_id>",
        BotChainDetailView.as_view(),
        name="bot-chain",
    ),
    path(
        "chain/<int:bot_id>",
        CreateChainView.as_view(),
        name="create-chain",
    ),
    path(
        "update-chain/<int:bot_id>/<int:chain_id>",
        UpdateChainView.as_view(),
        name="update-chain",
    ),
    path(
        "delete-chain/<int:bot_id>/<int:chain_id>",
        DeleteChainView.as_view(),
        name="delete-chain",
    ),
    path(
        "create-chain-step/<int:bot_id>/<int:chain_id>",
        CreateChainStepView.as_view(),
        name="create-chain-step",
    ),
    path(
        "update-chain-step/<int:bot_id>/<int:chain_id>/<int:step_id>",
        UpdateChainStepView.as_view(),
        name="update-chain-step",
    ),
    path(
        "delete-chain-step/<int:bot_id>/<int:chain_id>/<int:step_id>",
        DeleteChainStepView.as_view(),
        name="delete-chain-step",
    ),
]
