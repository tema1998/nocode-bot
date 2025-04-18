from unittest.mock import patch

from bots.models import Bot
from bots_mailing.services import MailingService
from bots_mailing.views import MailingView
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.messages.storage.fallback import FallbackStorage
from django.http import Http404
from django.test import RequestFactory, TestCase
from requests import RequestException


class MailingViewTestCase(TestCase):
    def setUp(self):
        """Set up the environment for MailingView tests, including a user and a bot."""
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="testuser", password="12345"
        )
        self.bot = Bot.objects.create(user=self.user, bot_id=123)

    def _add_messages_to_request(self, request):
        """Add message storage to the given request for testing message handling."""
        setattr(request, "session", "session")  # Mock session storage
        messages = FallbackStorage(request)  # Create a message storage
        setattr(
            request, "_messages", messages
        )  # Attach message storage to the request
        return request

    def test_get_authenticated(self):
        """Test GET request to MailingView when user is authenticated."""
        request = self.factory.get("/")  # Create a GET request
        request.user = self.user  # Assign the previously created user
        response = MailingView.as_view()(
            request, bot_id=self.bot.id
        )  # Call the view

        self.assertEqual(
            response.status_code, 200
        )  # Check for successful response
        if hasattr(response, "context_data"):
            self.assertIn(
                "bot", response.context_data
            )  # Ensure bot is in context
            self.assertEqual(
                response.context_data["bot"], self.bot
            )  # Check if the correct bot is returned

    def test_get_unauthenticated(self):
        """Test GET request to MailingView when user is unauthenticated."""
        request = self.factory.get("/")  # Create a GET request
        request.user = User()  # Assign an unauthenticated user
        with self.assertRaises(Http404):
            MailingView.as_view()(
                request, bot_id=self.bot.id
            )  # Ensure 404 is raised

    def test_get_nonexistent_bot(self):
        """Test GET request with a bot ID that does not exist."""
        request = self.factory.get("/")  # Create a GET request
        request.user = self.user  # Assign the user
        with self.assertRaises(Http404):
            MailingView.as_view()(request, bot_id=999)  # Ensure 404 is raised

    @patch("bots_mailing.services.MailingService.send_mailing")
    def test_post_success(self, mock_send_mailing):
        """Test successful mailing initiation via POST request."""
        mock_send_mailing.return_value = {
            "status": "success"
        }  # Mock success response

        request = self.factory.post(
            "/", {"message_text": "Test message"}
        )  # Create POST request
        request.user = self.user  # Assign user
        request = self._add_messages_to_request(
            request
        )  # Add messages to request

        response = MailingView.as_view()(
            request, bot_id=self.bot.id
        )  # Call the view

        messages_list = list(
            messages.get_messages(request)
        )  # Retrieve messages
        self.assertEqual(
            len(messages_list), 1
        )  # Ensure one message is present
        self.assertEqual(
            str(messages_list[0]), "Рассылка запущена."
        )  # Check the success message
        self.assertEqual(response.status_code, 302)  # Check for redirect
        self.assertEqual(
            response.url, f"/bots-mailing/bots/{self.bot.id}/mailing/"
        )  # Verify the redirect URL

    @patch("bots_mailing.services.MailingService.send_mailing")
    def test_post_failure(self, mock_send_mailing):
        """Test failure case for mailing initiation due to an API error."""
        mock_send_mailing.side_effect = RequestException(
            "API error"
        )  # Simulate API error

        request = self.factory.post(
            "/", {"message_text": "Test message"}
        )  # Create POST request
        request.user = self.user  # Assign user
        request = self._add_messages_to_request(
            request
        )  # Add messages to request

        response = MailingView.as_view()(
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
            "Ошибка запуска рассылки. Попробуйте повторить позже.",  # Check error message
        )
        self.assertEqual(response.status_code, 302)  # Check for redirect

    def test_post_empty_message(self):
        """Test mailing initiation with an empty message text."""
        request = self.factory.post(
            "/", {"message_text": ""}
        )  # Create POST request with empty message
        request.user = self.user  # Assign user
        request = self._add_messages_to_request(
            request
        )  # Add messages to request

        response = MailingView.as_view()(
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
            "Текст сообщения не может быть пустым.",  # Check empty message error
        )
        self.assertEqual(response.status_code, 302)  # Check for redirect


class MailingServiceTestCase(TestCase):
    @patch("requests.request")
    def test_send_mailing_success(self, mock_request):
        """Test successful mailing through the MailingService."""
        mock_response = mock_request.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "success"
        }  # Mock success response

        result = MailingService.send_mailing(
            123, "Test message"
        )  # Call the sending function

        self.assertEqual(result, {"status": "success"})  # Check return value
        mock_request.assert_called_once_with(
            "POST",
            f"{MailingService.BASE_URL}mailing/123/start/",  # Verify API endpoint
            json={"message": "Test message"},  # Verify payload
            timeout=15,
        )  # Check timeout setting

    @patch("requests.request")
    def test_send_mailing_api_error(self, mock_request):
        """Test mailing service failure due to an API error."""
        mock_request.side_effect = RequestException(
            "API error"
        )  # Simulate API error

        with self.assertRaises(RequestException):
            MailingService.send_mailing(
                123, "Test message"
            )  # Ensure exception is raised

    @patch("requests.request")
    def test_send_mailing_invalid_response(self, mock_request):
        """Test handling of an invalid response format from the API."""
        mock_response = mock_request.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = "invalid"  # Mock invalid response

        with self.assertRaises(ValueError):
            MailingService.send_mailing(
                123, "Test message"
            )  # Ensure exception is raised

    def test_send_mailing_empty_message(self):
        """Test error handling for sending a mailing with an empty message."""
        with self.assertRaises(ValueError):
            MailingService.send_mailing(
                123, ""
            )  # Ensure exception is raised for empty message
