import datetime
from unittest.mock import patch

from bots.models import Bot
from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone


class BotModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass"
        )

    def test_bot_creation(self):
        """Test bot model creation and fields"""
        test_datetime = timezone.make_aware(
            datetime.datetime(2023, 1, 1, 0, 0, 0)
        )

        with patch("django.utils.timezone.now") as mock_now:
            mock_now.return_value = test_datetime
            bot = Bot.objects.create(
                bot_username="test_bot", user=self.user, bot_id=123456
            )

        self.assertEqual(bot.bot_username, "test_bot")
        self.assertEqual(bot.user.username, "testuser")
        self.assertEqual(bot.bot_id, 123456)
        self.assertEqual(bot.created_at, test_datetime)

        # Compare naive datetime strings (without timezone)
        self.assertEqual(
            bot.created_at.strftime("%Y-%m-%d %H:%M:%S"), "2023-01-01 00:00:00"
        )

    def test_bot_str_representation(self):
        """Test string representation of bot model"""
        bot = Bot.objects.create(
            bot_username="test_bot", user=self.user, bot_id=123456
        )
        self.assertEqual(str(bot), "test_bot")
