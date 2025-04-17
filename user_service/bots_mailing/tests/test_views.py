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
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="testuser", password="12345"
        )
        self.bot = Bot.objects.create(user=self.user, bot_id=123)

    def _add_messages_to_request(self, request):
        setattr(request, "session", "session")
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)
        return request

    def test_get_authenticated(self):
        request = self.factory.get("/")
        request.user = self.user
        response = MailingView.as_view()(request, bot_id=self.bot.id)

        self.assertEqual(response.status_code, 200)
        if hasattr(response, "context_data"):
            self.assertIn("bot", response.context_data)
            self.assertEqual(response.context_data["bot"], self.bot)

    def test_get_unauthenticated(self):
        request = self.factory.get("/")
        request.user = User()  # Unauthenticated user
        with self.assertRaises(Http404):
            MailingView.as_view()(request, bot_id=self.bot.id)

    def test_get_nonexistent_bot(self):
        request = self.factory.get("/")
        request.user = self.user
        with self.assertRaises(Http404):
            MailingView.as_view()(request, bot_id=999)

    @patch("bots_mailing.services.MailingService.send_mailing")
    def test_post_success(self, mock_send_mailing):
        mock_send_mailing.return_value = {"status": "success"}

        request = self.factory.post("/", {"message_text": "Test message"})
        request.user = self.user
        request = self._add_messages_to_request(request)

        response = MailingView.as_view()(request, bot_id=self.bot.id)

        messages_list = list(messages.get_messages(request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(str(messages_list[0]), "Рассылка запущена.")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url, f"/bots-mailing/bots/{self.bot.id}/mailing/"
        )

    @patch("bots_mailing.services.MailingService.send_mailing")
    def test_post_failure(self, mock_send_mailing):
        mock_send_mailing.side_effect = RequestException("API error2")

        request = self.factory.post("/", {"message_text": "Test message"})
        request.user = self.user
        request = self._add_messages_to_request(request)

        response = MailingView.as_view()(request, bot_id=self.bot.id)

        messages_list = list(messages.get_messages(request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(
            str(messages_list[0]),
            "Failed to start mailing. Please try again later",
        )
        self.assertEqual(response.status_code, 302)

    def test_post_empty_message(self):
        request = self.factory.post("/", {"message_text": ""})
        request.user = self.user
        request = self._add_messages_to_request(request)

        response = MailingView.as_view()(request, bot_id=self.bot.id)

        messages_list = list(messages.get_messages(request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(str(messages_list[0]), "Message text cannot be empty")
        self.assertEqual(response.status_code, 302)


class MailingServiceTestCase(TestCase):
    @patch("requests.request")
    def test_send_mailing_success(self, mock_request):
        mock_response = mock_request.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}

        result = MailingService.send_mailing(123, "Test message")

        self.assertEqual(result, {"status": "success"})
        mock_request.assert_called_once_with(
            "POST",
            f"{MailingService.BASE_URL}mailing/123/start/",
            json={"message": "Test message"},
            timeout=15,
        )

    @patch("requests.request")
    def test_send_mailing_api_error(self, mock_request):
        mock_request.side_effect = RequestException("API error")

        with self.assertRaises(RequestException):
            MailingService.send_mailing(123, "Test message")

    @patch("requests.request")
    def test_send_mailing_invalid_response(self, mock_request):
        mock_response = mock_request.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = "invalid"  # Not a dict

        with self.assertRaises(ValueError):
            MailingService.send_mailing(123, "Test message")

    def test_send_mailing_empty_message(self):
        with self.assertRaises(ValueError):
            MailingService.send_mailing(123, "")
