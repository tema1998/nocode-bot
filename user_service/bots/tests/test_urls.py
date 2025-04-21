from bots.views import (
    AddBotView,
    BotDefaultReplyView,
    BotDeleteView,
    BotDetailView,
    BotsView,
    BotUsersView,
)
from django.test import SimpleTestCase
from django.urls import resolve, reverse


class TestUrls(SimpleTestCase):
    def test_bots_list_url_resolves(self):
        """Test that the URL for listing bots resolves to the BotsView."""
        url = reverse("bots")  # Generate the URL for the 'bots' view
        self.assertEqual(
            resolve(url).func.view_class, BotsView
        )  # Check that it resolves to the correct view
        self.assertEqual(
            url, "/bots/"
        )  # Ensure the constructed URL is as expected

    def test_add_bot_url_resolves(self):
        """Test that the URL for adding a bot resolves to the AddBotView."""
        url = reverse("add-bot")  # Generate the URL for the 'add-bot' view
        self.assertEqual(
            resolve(url).func.view_class, AddBotView
        )  # Verify the correct view is resolved
        self.assertEqual(
            url, "/bots/add/"
        )  # Check the constructed URL is as expected

    def test_bot_details_url_resolves(self):
        """Test that the URL for bot details resolves to the BotDetailView."""
        url = reverse("bot-detail", args=[1])  # Generate URL for bot with ID 1
        self.assertEqual(
            resolve(url).func.view_class, BotDetailView
        )  # Check resolution to the correct view
        self.assertEqual(url, "/bots/1/")  # Validate expected URL

    def test_bot_delete_url_resolves(self):
        """Test that the URL for deleting a bot resolves to the BotDeleteView."""
        url = reverse(
            "bot-delete", args=[1]
        )  # Generate URL to delete bot with ID 1
        self.assertEqual(
            resolve(url).func.view_class, BotDeleteView
        )  # Verify view resolution
        self.assertEqual(
            url, "/bots/1/delete/"
        )  # Assert expected URL is correct

    def test_bot_default_reply_url_resolves(self):
        """Test that the URL for setting a default reply resolves to the BotDefaultReplyView."""
        url = reverse(
            "bot-default-reply", args=[1]
        )  # Generate URL for default reply of bot with ID 1
        self.assertEqual(
            resolve(url).func.view_class, BotDefaultReplyView
        )  # Check correct view resolution
        self.assertEqual(url, "/bots/1/default-reply/")  # Assert expected URL

    def test_bot_users_url_resolves(self):
        """Test that the URL for viewing bot users resolves to the BotUsersView."""
        url = reverse(
            "bot-users", args=[1]
        )  # Generate URL for users of bot with ID 1
        self.assertEqual(
            resolve(url).func.view_class, BotUsersView
        )  # Verify resolution to the correct view
        self.assertEqual(url, "/bots/1/users/")  # Check expected URL

    def test_url_patterns(self):
        """Test that all relevant URL patterns resolve to their corresponding expected paths."""
        # Verify various URL patterns resolve correctly
        self.assertEqual(reverse("bots"), "/bots/")  # Bots list URL
        self.assertEqual(reverse("add-bot"), "/bots/add/")  # Add bot URL
        self.assertEqual(
            reverse("bot-detail", args=[5]), "/bots/5/"
        )  # Bot details for ID 5
        self.assertEqual(
            reverse("bot-delete", args=[10]), "/bots/10/delete/"
        )  # Delete bot for ID 10
        self.assertEqual(
            reverse("bot-default-reply", args=[7]),
            "/bots/7/default-reply/",  # Default reply for bot ID 7
        )
        self.assertEqual(
            reverse("bot-users", args=[3]), "/bots/3/users/"
        )  # Users of bot ID 3
