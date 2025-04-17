from bots_menu.views import (
    BotMainMenuButtonView,
    BotMainMenuView,
    CreateBotMainMenuButtonView,
    DeleteBotMainMenuButtonView,
    UpdateBotMainMenuButtonView,
)
from django.test import SimpleTestCase
from django.urls import resolve, reverse


class TestBotMainMenuUrls(SimpleTestCase):
    def test_bot_main_menu_url_resolves(self):
        url = reverse("bot-main-menu", args=[1])
        self.assertEqual(resolve(url).func.view_class, BotMainMenuView)
        self.assertEqual(url, "/bots-menu/main-menu/1")

    def test_bot_main_menu_button_url_resolves(self):
        url = reverse("bot-main-menu-button", args=[1, 2])
        self.assertEqual(resolve(url).func.view_class, BotMainMenuButtonView)
        self.assertEqual(url, "/bots-menu/main-menu-button/1/2")

    def test_update_main_menu_button_url_resolves(self):
        url = reverse("update-bot-main-menu-button", args=[1, 2])
        self.assertEqual(
            resolve(url).func.view_class, UpdateBotMainMenuButtonView
        )
        self.assertEqual(url, "/bots-menu/update-main-menu-button/1/2")

    def test_create_main_menu_button_url_resolves(self):
        url = reverse("create-bot-main-menu-button", args=[1])
        self.assertEqual(
            resolve(url).func.view_class, CreateBotMainMenuButtonView
        )
        self.assertEqual(url, "/bots-menu/create-main-menu-button/1")

    def test_delete_main_menu_button_url_resolves(self):
        url = reverse("delete-bot-main-menu-button", args=[1, 2])
        self.assertEqual(
            resolve(url).func.view_class, DeleteBotMainMenuButtonView
        )
        self.assertEqual(url, "/bots-menu/delete-main-menu-button/1/2")

    def test_url_patterns_with_different_ids(self):
        test_cases = [
            ("bot-main-menu", [5], "/bots-menu/main-menu/5"),
            (
                "bot-main-menu-button",
                [3, 7],
                "/bots-menu/main-menu-button/3/7",
            ),
            (
                "update-bot-main-menu-button",
                [4, 9],
                "/bots-menu/update-main-menu-button/4/9",
            ),
            (
                "create-bot-main-menu-button",
                [2],
                "/bots-menu/create-main-menu-button/2",
            ),
            (
                "delete-bot-main-menu-button",
                [8, 1],
                "/bots-menu/delete-main-menu-button/8/1",
            ),
        ]

        for name, args, expected_url in test_cases:
            with self.subTest(name=name, args=args):
                self.assertEqual(reverse(name, args=args), expected_url)
