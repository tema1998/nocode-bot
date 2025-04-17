from unittest.mock import patch

from bots.models import Bot
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory, TestCase
from requests import RequestException

from ..views import (
    BotMainMenuButtonView,
    CreateBotMainMenuButtonView,
    DeleteBotMainMenuButtonView,
    UpdateBotMainMenuButtonView,
)


class BotMainMenuButtonViewTestCase(TestCase):
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

    @patch(
        "user_service.bots_menu.views.BotServiceClient.get_main_menu_button"
    )
    @patch("user_service.bots_menu.views.BotServiceClient.get_bot_chains")
    def test_get_success(self, mock_get_chains, mock_get_button):
        mock_get_button.return_value = {"id": 1, "button_text": "Test"}
        mock_get_chains.return_value = {"chains": {"1": "Test Chain"}}

        request = self.factory.get("/")
        request.user = self.user
        response = BotMainMenuButtonView.as_view()(
            request, bot_id=self.bot.id, button_id=1
        )

        self.assertEqual(response.status_code, 200)
        if hasattr(response, "context_data"):
            self.assertIn("button", response.context_data)
            self.assertIn("chains", response.context_data)
            self.assertEqual(
                response.context_data["button"],
                {"id": 1, "button_text": "Test"},
            )
            self.assertEqual(
                response.context_data["chains"], {"1": "Test Chain"}
            )

    @patch(
        "user_service.bots_menu.views.BotServiceClient.get_main_menu_button"
    )
    @patch("user_service.bots_menu.views.BotServiceClient.get_bot_chains")
    def test_get_failure(self, mock_get_chains, mock_get_button):
        mock_get_button.side_effect = RequestException("API error")
        mock_get_chains.return_value = {"chains": {}}

        request = self.factory.get("/")
        request.user = self.user
        request = self._add_messages_to_request(request)

        response = BotMainMenuButtonView.as_view()(
            request, bot_id=self.bot.id, button_id=1
        )

        messages_list = list(messages.get_messages(request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(
            str(messages_list[0]),
            "Ошибка при загрузке данных. Попробуйте обновить страницу.",
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url, f"/bots-menu/main-menu-button/{self.bot.id}/1"
        )


class UpdateBotMainMenuButtonViewTestCase(TestCase):
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

    @patch(
        "user_service.bots_menu.views.BotServiceClient.update_main_menu_button"
    )
    def test_post_success(self, mock_update_button):
        mock_update_button.return_value = {}

        request = self.factory.post(
            "/",
            {
                "button_text": "New Button",
                "reply_text": "Reply",
                "chain_id": "1",
            },
        )
        request.user = self.user
        request = self._add_messages_to_request(request)

        response = UpdateBotMainMenuButtonView.as_view()(
            request, bot_id=self.bot.id, button_id=1
        )

        messages_list = list(messages.get_messages(request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(str(messages_list[0]), "Изменения сохранены.")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f"/bots-menu/main-menu/{self.bot.id}")

    @patch(
        "user_service.bots_menu.views.BotServiceClient.update_main_menu_button"
    )
    def test_post_failure(self, mock_update_button):
        mock_update_button.side_effect = RequestException("API error")

        request = self.factory.post(
            "/",
            {
                "button_text": "New Button",
                "reply_text": "Reply",
                "chain_id": "1",
            },
        )
        request.user = self.user
        request = self._add_messages_to_request(request)

        response = UpdateBotMainMenuButtonView.as_view()(
            request, bot_id=self.bot.id, button_id=1
        )

        messages_list = list(messages.get_messages(request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(
            str(messages_list[0]),
            "Ошибка при обновлении данных. Проверьте формат данных!",
        )
        self.assertEqual(response.status_code, 302)

    def test_post_invalid_form(self):
        request = self.factory.post("/", {})  # Empty data
        request.user = self.user
        request = self._add_messages_to_request(request)

        response = UpdateBotMainMenuButtonView.as_view()(
            request, bot_id=self.bot.id, button_id=1
        )

        messages_list = list(messages.get_messages(request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(
            str(messages_list[0]), "Проверьте правильность данных."
        )
        self.assertEqual(response.status_code, 302)


class CreateBotMainMenuButtonViewTestCase(TestCase):
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

    @patch("user_service.bots_menu.views.BotServiceClient.get_bot_chains")
    def test_get_success(self, mock_get_chains):
        mock_get_chains.return_value = {"chains": {"1": "Test Chain"}}

        request = self.factory.get("/")
        request.user = self.user
        response = CreateBotMainMenuButtonView.as_view()(
            request, bot_id=self.bot.id
        )

        self.assertEqual(response.status_code, 200)
        if hasattr(response, "context_data"):
            self.assertIn("chains", response.context_data)
            self.assertEqual(
                response.context_data["chains"], {"1": "Test Chain"}
            )

    @patch("user_service.bots_menu.views.BotServiceClient.get_bot_chains")
    def test_get_failure(self, mock_get_chains):
        mock_get_chains.side_effect = RequestException("API error")

        request = self.factory.get("/")
        request.user = self.user
        response = CreateBotMainMenuButtonView.as_view()(
            request, bot_id=self.bot.id
        )

        self.assertEqual(response.status_code, 200)
        if hasattr(response, "context_data"):
            self.assertIn("chains", response.context_data)
            self.assertEqual(response.context_data["chains"], {})

    @patch(
        "user_service.bots_menu.views.BotServiceClient.create_main_menu_button"
    )
    def test_post_success(self, mock_create_button):
        mock_create_button.return_value = {}

        request = self.factory.post(
            "/",
            {
                "button_text": "New Button",
                "reply_text": "Reply",
                "chain_id": "1",
            },
        )
        request.user = self.user
        request = self._add_messages_to_request(request)

        response = CreateBotMainMenuButtonView.as_view()(
            request, bot_id=self.bot.id
        )

        messages_list = list(messages.get_messages(request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(str(messages_list[0]), "Кнопка успешно создана.")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f"/bots-menu/main-menu/{self.bot.id}")

    @patch(
        "user_service.bots_menu.views.BotServiceClient.create_main_menu_button"
    )
    def test_post_failure(self, mock_create_button):
        mock_create_button.side_effect = RequestException("API error")

        request = self.factory.post(
            "/",
            {
                "button_text": "New Button",
                "reply_text": "Reply",
                "chain_id": "1",
            },
        )
        request.user = self.user
        request = self._add_messages_to_request(request)

        response = CreateBotMainMenuButtonView.as_view()(
            request, bot_id=self.bot.id
        )

        messages_list = list(messages.get_messages(request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(
            str(messages_list[0]),
            "Ошибка при создании кнопки. Возможно такая кнопка уже существует. Запрещено использовать названия служебных команд '/start', '/update'.",
        )
        self.assertEqual(response.status_code, 302)

    def test_post_invalid_form(self):
        request = self.factory.post("/", {})  # Empty data
        request.user = self.user
        request = self._add_messages_to_request(request)

        response = CreateBotMainMenuButtonView.as_view()(
            request, bot_id=self.bot.id
        )

        messages_list = list(messages.get_messages(request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(
            str(messages_list[0]), "Проверьте правильность данных."
        )
        self.assertEqual(response.status_code, 302)


class DeleteBotMainMenuButtonViewTestCase(TestCase):
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

    @patch(
        "user_service.bots_menu.views.BotServiceClient.delete_main_menu_button"
    )
    def test_post_success(self, mock_delete_button):
        mock_delete_button.return_value = None

        request = self.factory.post("/")
        request.user = self.user
        request = self._add_messages_to_request(request)

        response = DeleteBotMainMenuButtonView.as_view()(
            request, bot_id=self.bot.id, button_id=1
        )

        messages_list = list(messages.get_messages(request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(str(messages_list[0]), "Кнопка успешно удалена.")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f"/bots-menu/main-menu/{self.bot.id}")

    @patch(
        "user_service.bots_menu.views.BotServiceClient.delete_main_menu_button"
    )
    def test_post_failure(self, mock_delete_button):
        mock_delete_button.side_effect = RequestException("API error")

        request = self.factory.post("/")
        request.user = self.user
        request = self._add_messages_to_request(request)

        response = DeleteBotMainMenuButtonView.as_view()(
            request, bot_id=self.bot.id, button_id=1
        )

        messages_list = list(messages.get_messages(request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(
            str(messages_list[0]),
            "Ошибка при удалении кнопки. Попробуйте позже.",
        )
        self.assertEqual(response.status_code, 302)
