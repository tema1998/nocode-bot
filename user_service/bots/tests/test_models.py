import datetime
from unittest.mock import patch

from bots.models import Bot
from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone


class BotModelTest(TestCase):
    def setUp(self):
        """Set up the test environment by creating a user."""
        self.user = User.objects.create_user(
            username="testuser", password="testpass"
        )

    def test_bot_creation(self):
        """Test the creation of a Bot model instance and validate its fields."""
        # Create a specific datetime for testing
        test_datetime = timezone.make_aware(
            datetime.datetime(2023, 1, 1, 0, 0, 0)
        )

        # Patch the timezone.now() method to return the specific datetime defined above
        with patch("django.utils.timezone.now") as mock_now:
            mock_now.return_value = (
                test_datetime  # Set mock's return value to test_datetime
            )
            bot = Bot.objects.create(
                bot_username="test_bot", user=self.user, bot_id=123456
            )

        # Assertions to validate the bot's fields
        self.assertEqual(bot.bot_username, "test_bot")  # Check bot username
        self.assertEqual(
            bot.user.username, "testuser"
        )  # Check associated user's username
        self.assertEqual(bot.bot_id, 123456)  # Check bot ID
        self.assertEqual(
            bot.created_at, test_datetime
        )  # Check creation timestamp matches the mocked time

        # Validate the string representation of the created_at datetime
        self.assertEqual(
            bot.created_at.strftime("%Y-%m-%d %H:%M:%S"), "2023-01-01 00:00:00"
        )

    def test_bot_str_representation(self):
        """Test the string representation method of the Bot model."""
        # Create a Bot instance
        bot = Bot.objects.create(
            bot_username="test_bot", user=self.user, bot_id=123456
        )

        # Assert that the string representation returns the bot's username
        self.assertEqual(str(bot), "test_bot")
