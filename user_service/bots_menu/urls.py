from django.urls import include, path

from .views import (
    BotMainMenuButtonView,
    BotMainMenuView,
    CreateBotMainMenuButtonView,
    DeleteBotMainMenuButtonView,
    UpdateBotMainMenuButtonView,
)


urlpatterns = [
    path(
        "bots/<int:bot_id>/menu/",
        include(
            [
                path("", BotMainMenuView.as_view(), name="menu-main"),
                path(
                    "buttons/",
                    include(
                        [
                            path(
                                "",
                                CreateBotMainMenuButtonView.as_view(),
                                name="menu-button-create",
                            ),
                            path(
                                "<int:button_id>/",
                                include(
                                    [
                                        path(
                                            "",
                                            BotMainMenuButtonView.as_view(),
                                            name="menu-button-detail",
                                        ),
                                        path(
                                            "update/",
                                            UpdateBotMainMenuButtonView.as_view(),
                                            name="menu-button-update",
                                        ),
                                        path(
                                            "delete/",
                                            DeleteBotMainMenuButtonView.as_view(),
                                            name="menu-button-delete",
                                        ),
                                    ]
                                ),
                            ),
                        ]
                    ),
                ),
            ]
        ),
    ),
]
