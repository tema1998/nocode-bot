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
        """Set up the base environment for bot view tests, including a user and a bot."""
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="testuser", password="12345"
        )
        self.bot = Bot.objects.create(
            user=self.user, bot_id=123, bot_username="test_bot"
        )

    def _add_messages_to_request(self, request):
        """Add message storage to the given request for testing message handling."""
        setattr(request, "session", "session")  # Mock session attribute
        messages = FallbackStorage(request)  # Create message storage
        setattr(
            request, "_messages", messages
        )  # Attach messages to the request
        return request


class BotsViewTestCase(TestCase):
    def setUp(self):
        """Set up the environment for BotsView test, including a user."""
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="testuser", password="12345"
        )

    def test_get_authenticated(self):
        """Test GET request to BotsView when user is authenticated."""
        request = self.factory.get("/")  # Create a GET request
        request.user = self.user  # Assign the previously created user
        Bot.objects.create(user=self.user, bot_id=123, bot_username="test_bot")

        response = BotsView.as_view()(request)  # Call the view

        self.assertEqual(
            response.status_code, 200
        )  # Check for successful response
        if hasattr(response, "context_data"):
            self.assertEqual(
                len(response.context_data["bots"]), 1
            )  # Ensure one bot is in context


class BotDetailViewTestCase(BaseBotViewTestCase):
    @patch("bots.services.BotService.get_bot_details")
    def test_get_success(self, mock_get_details):
        """Test successful retrieval of bot details."""
        mock_get_details.return_value = {
            "username": "test_bot",
            "is_active": True,
        }

        request = self.factory.get("/")  # Create a GET request
        request.user = self.user  # Assign user
        response = BotDetailView.as_view()(
            request, bot_id=self.bot.id
        )  # Call the bot detail view

        self.assertEqual(response.status_code, 200)  # Check status code
        if hasattr(response, "context_data"):
            self.assertEqual(
                response.context_data["bot_data"]["username"], "test_bot"
            )  # Verify expected bot username in context

    @patch("bots.services.BotService.get_bot_details")
    def test_get_failure(self, mock_get_details):
        """Test failure case when retrieving bot details due to an API error."""
        mock_get_details.side_effect = RequestException(
            "API error"
        )  # Simulate API error

        request = self.factory.get("/")  # Create a GET request
        request.user = self.user  # Assign user
        response = BotDetailView.as_view()(
            request, bot_id=self.bot.id
        )  # Call view

        self.assertEqual(response.status_code, 200)  # Check status code
        if hasattr(response, "context_data"):
            self.assertTrue(
                response.context_data["bot_data"]["token_error"]
            )  # Check for error flag in context

    @patch("bots.services.BotService.update_bot")
    def test_post_success(self, mock_update_bot):
        """Test successful bot update via POST request."""
        mock_update_bot.return_value = {
            "username": "updated_bot"
        }  # Mock update response

        request = self.factory.post(
            "/",
            {
                "token": "1234567890:ABCdefGHIJKlmnOpQRSTuvwXYZ",
                "is_active": "on",
            },
        )
        request.user = self.user  # Assign user
        request = self._add_messages_to_request(
            request
        )  # Add messages to request

        response = BotDetailView.as_view()(
            request, bot_id=self.bot.id
        )  # Call the view

        messages_list = list(
            messages.get_messages(request)
        )  # Retrieve messages
        self.assertEqual(
            len(messages_list), 1
        )  # Ensure one message is present
        self.assertEqual(
            str(messages_list[0]), "Данные бота успешно обновлены."
        )  # Check the success message
        self.assertEqual(response.status_code, 302)  # Check for redirect

    @patch("bots.services.BotService.update_bot")
    def test_post_failure(self, mock_update_bot):
        """Test failed bot update when the service raises an exception."""
        mock_update_bot.side_effect = RequestException(
            "API error"
        )  # Simulate failure

        request = self.factory.post(
            "/", {"token": "1234567890:ABCdefGHIJKlmnOpQRSTuvwXYZ"}
        )
        request.user = self.user  # Assign user
        request = self._add_messages_to_request(
            request
        )  # Add messages to request

        response = BotDetailView.as_view()(
            request, bot_id=self.bot.id
        )  # Call the view

        messages_list = list(
            messages.get_messages(request)
        )  # Retrieve messages
        self.assertEqual(
            len(messages_list), 1
        )  # Ensure one message is present
        self.assertTrue(
            "Ошибка при обновлении данных" in str(messages_list[0])
        )  # Check error message
        self.assertEqual(response.status_code, 302)  # Check for redirect


class BotDeleteViewTestCase(BaseBotViewTestCase):
    @patch("bots.services.BotService.delete_bot")
    def test_post_success(self, mock_delete_bot):
        """Test successful bot deletion via POST request."""
        mock_delete_bot.return_value = None  # Mock successful deletion

        request = self.factory.post("/")  # Create POST request
        request.user = self.user  # Assign user
        request = self._add_messages_to_request(
            request
        )  # Add messages to request

        response = BotDeleteView.as_view()(
            request, bot_id=self.bot.id
        )  # Call the view

        messages_list = list(
            messages.get_messages(request)
        )  # Retrieve messages
        self.assertEqual(
            len(messages_list), 1
        )  # Ensure one message is present
        self.assertEqual(
            str(messages_list[0]),
            f"Бот @{self.bot.bot_username} успешно удален.",
        )  # Check success message
        self.assertEqual(response.status_code, 302)  # Check for redirect
        self.assertEqual(response.url, "/bots/")  # Check redirect URL

    @patch("bots.services.BotService.delete_bot")
    def test_post_failure(self, mock_delete_bot):
        """Test failed bot deletion when the service raises an exception."""
        mock_delete_bot.side_effect = RequestException(
            "API error"
        )  # Simulate failure

        request = self.factory.post("/")  # Create POST request
        request.user = self.user  # Assign user
        request = self._add_messages_to_request(
            request
        )  # Add messages to request

        response = BotDeleteView.as_view()(
            request, bot_id=self.bot.id
        )  # Call the view

        messages_list = list(
            messages.get_messages(request)
        )  # Retrieve messages
        self.assertEqual(
            len(messages_list), 1
        )  # Ensure one message is present
        self.assertEqual(
            str(messages_list[0]), "Ошибка при удалении бота."
        )  # Check error message
        self.assertEqual(response.status_code, 302)  # Check for redirect
        self.assertEqual(
            response.url, f"/bots/{self.bot.id}/"
        )  # Ensure redirect to the correct URL


class AddBotViewTestCase(TestCase):
    def setUp(self):
        """Set up the environment for AddBotView test, including a user."""
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="testuser", password="12345"
        )

    @patch("bots.services.BotService.create_bot")
    def test_form_valid(self, mock_create_bot):
        """Test successful creation of a new bot."""
        mock_create_bot.return_value = {
            "id": 123,
            "username": "new_bot",
        }  # Mock response for bot creation

        request = self.factory.post(
            "/", {"token": "1234567890:ABCdefGHIJKlmnOpQRSTuvwXYZ"}
        )
        request.user = self.user  # Assign user

        response = AddBotView.as_view()(request)  # Call the view

        self.assertEqual(response.status_code, 302)  # Check for redirect
        self.assertEqual(Bot.objects.count(), 1)  # Ensure one bot is created


class BotDefaultReplyViewTestCase(BaseBotViewTestCase):
    @patch("bots.services.BotService.get_bot_details")
    def test_get_success(self, mock_get_details):
        """Test successful retrieval of bot's default reply."""
        mock_get_details.return_value = {
            "default_reply": "Test reply"
        }  # Mock response for bot details

        request = self.factory.get("/")  # Create a GET request
        request.user = self.user  # Assign user
        response = BotDefaultReplyView.as_view()(
            request, bot_id=self.bot.id
        )  # Call the view

        self.assertEqual(response.status_code, 200)  # Check status code
        if hasattr(response, "context_data"):
            self.assertEqual(
                response.context_data["bot_data"]["default_reply"],
                "Test reply",
            )  # Verify default reply in context

    @patch("bots.services.BotService.update_bot")
    def test_post_success(self, mock_update_bot):
        """Test successful update of bot's default reply via POST request."""
        mock_update_bot.return_value = {}  # Mock successful update

        request = self.factory.post(
            "/", {"default_reply": "New reply"}
        )  # Create POST request
        request.user = self.user  # Assign user
        request = self._add_messages_to_request(
            request
        )  # Add messages to request

        response = BotDefaultReplyView.as_view()(
            request, bot_id=self.bot.id
        )  # Call the view

        messages_list = list(
            messages.get_messages(request)
        )  # Retrieve messages
        self.assertEqual(
            len(messages_list), 1
        )  # Ensure one message is present
        self.assertEqual(
            str(messages_list[0]), "Успешно обновлено."
        )  # Check success message
        self.assertEqual(response.status_code, 302)  # Check for redirect

    @patch("bots.services.BotService.update_bot")
    def test_post_failure(self, mock_update_bot):
        """Test failed update of bot's default reply when the service raises an exception."""
        mock_update_bot.side_effect = RequestException(
            "API error"
        )  # Simulate failure

        request = self.factory.post(
            "/", {"default_reply": "New reply"}
        )  # Create POST request
        request.user = self.user  # Assign user
        request = self._add_messages_to_request(
            request
        )  # Add messages to request

        response = BotDefaultReplyView.as_view()(
            request, bot_id=self.bot.id
        )  # Call the view

        messages_list = list(
            messages.get_messages(request)
        )  # Retrieve messages
        self.assertEqual(
            len(messages_list), 1
        )  # Ensure one message is present
        self.assertTrue(
            "Ошибка при обновлении данных" in str(messages_list[0])
        )  # Check error message
        self.assertEqual(response.status_code, 302)  # Check for redirect


class BotUsersViewTestCase(BaseBotViewTestCase):
    @patch("bots.services.BotUserService.get_bot_users")
    def test_get_success(self, mock_get_users):
        """Test successful retrieval of bot users."""
        mock_get_users.return_value = [
            {"id": 1, "username": "user1"}
        ]  # Mock response for user retrieval

        request = self.factory.get("/")  # Create a GET request
        request.user = self.user  # Assign user
        response = BotUsersView.as_view()(
            request, bot_id=self.bot.id
        )  # Call the view

        self.assertEqual(response.status_code, 200)  # Check status code
        if hasattr(response, "context_data"):
            self.assertEqual(
                len(response.context_data["page_obj"].object_list), 1
            )  # Validate that one user is present in context

    @patch("bots.services.BotUserService.get_bot_users")
    def test_get_empty(self, mock_get_users):
        """Test retrieval of bot users when there are none."""
        mock_get_users.return_value = []  # Mock empty response

        request = self.factory.get("/")  # Create a GET request
        request.user = self.user  # Assign user
        response = BotUsersView.as_view()(
            request, bot_id=self.bot.id
        )  # Call the view

        self.assertEqual(response.status_code, 200)  # Check status code
        if hasattr(response, "context_data"):
            self.assertIsNone(
                response.context_data["page_obj"]
            )  # Ensure page_obj is None for empty response
