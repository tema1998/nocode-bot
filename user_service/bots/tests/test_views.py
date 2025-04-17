from unittest.mock import MagicMock, patch

from bots.models import Bot
from bots.services import BotService, BotUserService
from bots.views import (
    AddBotView,
    BotDefaultReplyView,
    BotDeleteView,
    BotDetailView,
    BotsView,
    BotUsersView,
)
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.exceptions import ValidationError
from django.test import RequestFactory, TestCase
from requests import RequestException


class BaseBotViewTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="testuser", password="12345"
        )
        self.bot = Bot.objects.create(
            user=self.user, bot_id=123, bot_username="test_bot"
        )

    def _add_messages_to_request(self, request):
        setattr(request, "session", "session")
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)
        return request


class BotsViewTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="testuser", password="12345"
        )

    def test_get_authenticated(self):
        request = self.factory.get("/")
        request.user = self.user
        Bot.objects.create(user=self.user, bot_id=123, bot_username="test_bot")

        response = BotsView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        if hasattr(response, "context_data"):
            self.assertEqual(len(response.context_data["bots"]), 1)


class BotDetailViewTestCase(BaseBotViewTestCase):
    @patch("bots.services.BotService.get_bot_details")
    def test_get_success(self, mock_get_details):
        mock_get_details.return_value = {
            "username": "test_bot",
            "is_active": True,
        }

        request = self.factory.get("/")
        request.user = self.user
        response = BotDetailView.as_view()(request, bot_id=self.bot.id)

        self.assertEqual(response.status_code, 200)
        if hasattr(response, "context_data"):
            self.assertEqual(
                response.context_data["bot_data"]["username"], "test_bot"
            )

    @patch("bots.services.BotService.get_bot_details")
    def test_get_failure(self, mock_get_details):
        mock_get_details.side_effect = RequestException("API error")

        request = self.factory.get("/")
        request.user = self.user
        response = BotDetailView.as_view()(request, bot_id=self.bot.id)

        self.assertEqual(response.status_code, 200)
        if hasattr(response, "context_data"):
            self.assertTrue(response.context_data["bot_data"]["token_error"])

    @patch("bots.services.BotService.update_bot")
    def test_post_success(self, mock_update_bot):
        mock_update_bot.return_value = {"username": "updated_bot"}

        request = self.factory.post(
            "/",
            {
                "token": "1234567890:ABCdefGHIJKlmnOpQRSTuvwXYZ",
                "is_active": "on",
            },
        )
        request.user = self.user
        request = self._add_messages_to_request(request)

        response = BotDetailView.as_view()(request, bot_id=self.bot.id)

        messages_list = list(messages.get_messages(request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(
            str(messages_list[0]), "Данные бота успешно обновлены."
        )
        self.assertEqual(response.status_code, 302)

    @patch("bots.services.BotService.update_bot")
    def test_post_failure(self, mock_update_bot):
        mock_update_bot.side_effect = RequestException("API error")

        request = self.factory.post(
            "/", {"token": "1234567890:ABCdefGHIJKlmnOpQRSTuvwXYZ"}
        )
        request.user = self.user
        request = self._add_messages_to_request(request)

        response = BotDetailView.as_view()(request, bot_id=self.bot.id)

        messages_list = list(messages.get_messages(request))
        self.assertEqual(len(messages_list), 1)
        self.assertTrue(
            "Ошибка при обновлении данных" in str(messages_list[0])
        )
        self.assertEqual(response.status_code, 302)


class BotDeleteViewTestCase(BaseBotViewTestCase):
    @patch("bots.services.BotService.delete_bot")
    def test_post_success(self, mock_delete_bot):
        mock_delete_bot.return_value = None

        request = self.factory.post("/")
        request.user = self.user
        request = self._add_messages_to_request(request)

        response = BotDeleteView.as_view()(request, bot_id=self.bot.id)

        messages_list = list(messages.get_messages(request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(
            str(messages_list[0]),
            f"Бот @{self.bot.bot_username} успешно удален.",
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/bots/")

    @patch("bots.services.BotService.delete_bot")
    def test_post_failure(self, mock_delete_bot):
        mock_delete_bot.side_effect = RequestException("API error")

        request = self.factory.post("/")
        request.user = self.user
        request = self._add_messages_to_request(request)

        response = BotDeleteView.as_view()(request, bot_id=self.bot.id)

        messages_list = list(messages.get_messages(request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(str(messages_list[0]), "Ошибка при удалении бота.")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f"/bots/{self.bot.id}")


class AddBotViewTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="testuser", password="12345"
        )

    @patch("bots.services.BotService.create_bot")
    def test_form_valid(self, mock_create_bot):
        mock_create_bot.return_value = {"id": 123, "username": "new_bot"}

        request = self.factory.post(
            "/", {"token": "1234567890:ABCdefGHIJKlmnOpQRSTuvwXYZ"}
        )
        request.user = self.user

        response = AddBotView.as_view()(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Bot.objects.count(), 1)


class BotDefaultReplyViewTestCase(BaseBotViewTestCase):
    @patch("bots.services.BotService.get_bot_details")
    def test_get_success(self, mock_get_details):
        mock_get_details.return_value = {"default_reply": "Test reply"}

        request = self.factory.get("/")
        request.user = self.user
        response = BotDefaultReplyView.as_view()(request, bot_id=self.bot.id)

        self.assertEqual(response.status_code, 200)
        if hasattr(response, "context_data"):
            self.assertEqual(
                response.context_data["bot_data"]["default_reply"],
                "Test reply",
            )

    @patch("bots.services.BotService.update_bot")
    def test_post_success(self, mock_update_bot):
        mock_update_bot.return_value = {}

        request = self.factory.post("/", {"default_reply": "New reply"})
        request.user = self.user
        request = self._add_messages_to_request(request)

        response = BotDefaultReplyView.as_view()(request, bot_id=self.bot.id)

        messages_list = list(messages.get_messages(request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(str(messages_list[0]), "Успешно обновлено.")
        self.assertEqual(response.status_code, 302)

    @patch("bots.services.BotService.update_bot")
    def test_post_failure(self, mock_update_bot):
        mock_update_bot.side_effect = RequestException("API error")

        request = self.factory.post("/", {"default_reply": "New reply"})
        request.user = self.user
        request = self._add_messages_to_request(request)

        response = BotDefaultReplyView.as_view()(request, bot_id=self.bot.id)

        messages_list = list(messages.get_messages(request))
        self.assertEqual(len(messages_list), 1)
        self.assertTrue(
            "Ошибка при обновлении данных" in str(messages_list[0])
        )
        self.assertEqual(response.status_code, 302)


class BotUsersViewTestCase(BaseBotViewTestCase):
    @patch("bots.services.BotUserService.get_bot_users")
    def test_get_success(self, mock_get_users):
        mock_get_users.return_value = [{"id": 1, "username": "user1"}]

        request = self.factory.get("/")
        request.user = self.user
        response = BotUsersView.as_view()(request, bot_id=self.bot.id)

        self.assertEqual(response.status_code, 200)
        if hasattr(response, "context_data"):
            self.assertEqual(
                len(response.context_data["page_obj"].object_list), 1
            )

    @patch("bots.services.BotUserService.get_bot_users")
    def test_get_empty(self, mock_get_users):
        mock_get_users.return_value = []

        request = self.factory.get("/")
        request.user = self.user
        response = BotUsersView.as_view()(request, bot_id=self.bot.id)

        self.assertEqual(response.status_code, 200)
        if hasattr(response, "context_data"):
            self.assertIsNone(response.context_data["page_obj"])
