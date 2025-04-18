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
        """Test that the bot main menu URL resolves to the correct view."""
        url = reverse("bot-main-menu", args=[1])  # Generate URL with bot ID 1
        self.assertEqual(
            resolve(url).func.view_class, BotMainMenuView
        )  # Check resolution to BotMainMenuView
        self.assertEqual(
            url, "/bots-menu/main-menu/1"
        )  # Ensure the generated URL is as expected

    def test_bot_main_menu_button_url_resolves(self):
        """Test that the bot main menu button URL resolves to the correct view."""
        url = reverse(
            "bot-main-menu-button", args=[1, 2]
        )  # Generate URL with bot ID 1 and button ID 2
        self.assertEqual(
            resolve(url).func.view_class, BotMainMenuButtonView
        )  # Check resolution to BotMainMenuButtonView
        self.assertEqual(
            url, "/bots-menu/main-menu-button/1/2"
        )  # Ensure the generated URL is as expected

    def test_update_main_menu_button_url_resolves(self):
        """Test that the update main menu button URL resolves to the correct view."""
        url = reverse(
            "update-bot-main-menu-button", args=[1, 2]
        )  # Generate URL for updating button
        self.assertEqual(
            resolve(url).func.view_class, UpdateBotMainMenuButtonView
        )  # Check resolution to UpdateBotMainMenuButtonView
        self.assertEqual(
            url, "/bots-menu/update-main-menu-button/1/2"
        )  # Ensure the generated URL is as expected

    def test_create_main_menu_button_url_resolves(self):
        """Test that the create main menu button URL resolves to the correct view."""
        url = reverse(
            "create-bot-main-menu-button", args=[1]
        )  # Generate URL for creating button
        self.assertEqual(
            resolve(url).func.view_class, CreateBotMainMenuButtonView
        )  # Check resolution to CreateBotMainMenuButtonView
        self.assertEqual(
            url, "/bots-menu/create-main-menu-button/1"
        )  # Ensure the generated URL is as expected

    def test_delete_main_menu_button_url_resolves(self):
        """Test that the delete main menu button URL resolves to the correct view."""
        url = reverse(
            "delete-bot-main-menu-button", args=[1, 2]
        )  # Generate URL for deleting button
        self.assertEqual(
            resolve(url).func.view_class, DeleteBotMainMenuButtonView
        )  # Check resolution to DeleteBotMainMenuButtonView
        self.assertEqual(
            url, "/bots-menu/delete-main-menu-button/1/2"
        )  # Ensure the generated URL is as expected

    def test_url_patterns_with_different_ids(self):
        """Test URL patterns generation with various IDs."""
        test_cases = [
            (
                "bot-main-menu",
                [5],
                "/bots-menu/main-menu/5",
            ),  # Test bot main menu for ID 5
            (
                "bot-main-menu-button",
                [3, 7],
                "/bots-menu/main-menu-button/3/7",
            ),  # Test main menu button for bot ID 3 and button ID 7
            (
                "update-bot-main-menu-button",
                [4, 9],
                "/bots-menu/update-main-menu-button/4/9",
            ),  # Test updating button
            (
                "create-bot-main-menu-button",
                [2],
                "/bots-menu/create-main-menu-button/2",
            ),  # Test creating button for bot ID 2
            (
                "delete-bot-main-menu-button",
                [8, 1],
                "/bots-menu/delete-main-menu-button/8/1",
            ),  # Test deleting button
        ]

        # Iterate through the test cases to ensure each URL resolves correctly
        for name, args, expected_url in test_cases:
            with self.subTest(
                name=name, args=args
            ):  # Create a sub-test for each case
                self.assertEqual(
                    reverse(name, args=args), expected_url
                )  # Check generated URL matches expected URL
