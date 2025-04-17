from unittest.mock import MagicMock, patch

from bots.models import Bot
from bots_chain.services import (
    ChainButtonService,
    ChainService,
    ChainStepService,
)
from bots_chain.types import ChainButtonData, ChainData, ChainStepData
from bots_chain.views import *
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory, TestCase
from requests import RequestException


class BaseChainViewTestCase(TestCase):
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


class BotChainViewTestCase(BaseChainViewTestCase):
    @patch("bots_chain.services.ChainService.get_bot_chains")
    def test_get_success(self, mock_get_chains):
        mock_get_chains.return_value = {
            "chains": [{"id": 1, "name": "Test Chain"}]
        }

        request = self.factory.get("/")
        request.user = self.user
        response = BotChainView.as_view()(request, bot_id=self.bot.id)

        self.assertEqual(response.status_code, 200)
        if hasattr(response, "context_data"):
            self.assertIn("chains", response.context_data)
            self.assertEqual(
                response.context_data["chains"],
                [{"id": 1, "name": "Test Chain"}],
            )

    @patch("bots_chain.services.ChainService.get_bot_chains")
    def test_get_failure(self, mock_get_chains):
        mock_get_chains.side_effect = RequestException("API error")

        request = self.factory.get("/")
        request.user = self.user
        response = BotChainView.as_view()(request, bot_id=self.bot.id)

        self.assertEqual(response.status_code, 200)
        if hasattr(response, "context_data"):
            self.assertEqual(response.context_data["chains"], [])


class BotChainDetailViewTestCase(BaseChainViewTestCase):
    @patch("bots_chain.services.ChainService.get_chain")
    def test_get_success(self, mock_get_chain):
        chain_data = {"id": 1, "name": "Test Chain"}
        mock_get_chain.return_value = chain_data

        request = self.factory.get("/")
        request.user = self.user
        response = BotChainDetailView.as_view()(
            request, bot_id=self.bot.id, chain_id=1
        )

        self.assertEqual(response.status_code, 200)
        if hasattr(response, "context_data"):
            self.assertEqual(response.context_data["chain"], chain_data)
            self.assertEqual(
                json.loads(response.context_data["chain_json"]), chain_data
            )

    @patch("bots_chain.services.ChainService.get_chain")
    def test_get_failure(self, mock_get_chain):
        mock_get_chain.side_effect = RequestException("API error")

        request = self.factory.get("/")
        request.user = self.user
        response = BotChainDetailView.as_view()(
            request, bot_id=self.bot.id, chain_id=1
        )

        self.assertEqual(response.status_code, 200)
        if hasattr(response, "context_data"):
            self.assertEqual(
                response.context_data["chain"], {"id": 0, "name": ""}
            )
            self.assertEqual(response.context_data["chain_json"], "{}")


class CreateChainViewTestCase(BaseChainViewTestCase):
    @patch("bots_chain.services.ChainService.create_chain")
    def test_post_success(self, mock_create_chain):
        mock_create_chain.return_value = {"id": 1, "name": "New Chain"}

        request = self.factory.post("/", {"name": "New Chain"})
        request.user = self.user
        request = self._add_messages_to_request(request)

        response = CreateChainView.as_view()(request, bot_id=self.bot.id)

        messages_list = list(messages.get_messages(request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(str(messages_list[0]), "Chain created successfully.")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f"/bots-chain/chains/{self.bot.id}/")

    @patch("bots_chain.services.ChainService.create_chain")
    def test_post_failure(self, mock_create_chain):
        mock_create_chain.side_effect = RequestException("API error")

        request = self.factory.post("/", {"name": "New Chain"})
        request.user = self.user
        request = self._add_messages_to_request(request)

        response = CreateChainView.as_view()(request, bot_id=self.bot.id)

        messages_list = list(messages.get_messages(request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(str(messages_list[0]), "Failed to create chain.")
        self.assertEqual(response.status_code, 302)


class UpdateChainViewTestCase(BaseChainViewTestCase):
    @patch("bots_chain.services.ChainService.update_chain")
    def test_post_success(self, mock_update_chain):
        mock_update_chain.return_value = {"id": 1, "name": "Updated Chain"}

        request = self.factory.post("/", {"name": "Updated Chain"})
        request.user = self.user
        request = self._add_messages_to_request(request)

        response = UpdateChainView.as_view()(
            request, bot_id=self.bot.id, chain_id=1
        )

        messages_list = list(messages.get_messages(request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(str(messages_list[0]), "Chain updated successfully.")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f"/bots-chain/chain/{self.bot.id}/1")

    @patch("bots_chain.services.ChainService.update_chain")
    def test_post_failure(self, mock_update_chain):
        mock_update_chain.side_effect = RequestException("API error")

        request = self.factory.post("/", {"name": "Updated Chain"})
        request.user = self.user
        request = self._add_messages_to_request(request)

        response = UpdateChainView.as_view()(
            request, bot_id=self.bot.id, chain_id=1
        )

        messages_list = list(messages.get_messages(request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(str(messages_list[0]), "Failed to update chain.")
        self.assertEqual(response.status_code, 302)


class DeleteChainViewTestCase(BaseChainViewTestCase):
    @patch("bots_chain.services.ChainService.delete_chain")
    def test_post_success(self, mock_delete_chain):
        mock_delete_chain.return_value = True

        request = self.factory.post("/")
        request.user = self.user
        request = self._add_messages_to_request(request)

        response = DeleteChainView.as_view()(
            request, bot_id=self.bot.id, chain_id=1
        )

        messages_list = list(messages.get_messages(request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(str(messages_list[0]), "Chain deleted successfully.")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f"/bots-chain/chains/{self.bot.id}/")

    @patch("bots_chain.services.ChainService.delete_chain")
    def test_post_failure(self, mock_delete_chain):
        mock_delete_chain.side_effect = RequestException("API error")

        request = self.factory.post("/")
        request.user = self.user
        request = self._add_messages_to_request(request)

        response = DeleteChainView.as_view()(
            request, bot_id=self.bot.id, chain_id=1
        )

        messages_list = list(messages.get_messages(request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(str(messages_list[0]), "Failed to delete chain.")
        self.assertEqual(response.status_code, 302)


class ChainStepViewsTestCase(BaseChainViewTestCase):
    @patch("bots_chain.services.ChainStepService.create_step")
    def test_create_step_success(self, mock_create_step):
        mock_create_step.return_value = {"id": 1, "name": "New Step"}

        request = self.factory.post(
            "/", {"set_as_next_step_for_button_id": "1"}
        )
        request.user = self.user
        request = self._add_messages_to_request(request)

        response = CreateChainStepView.as_view()(
            request, bot_id=self.bot.id, chain_id=1
        )

        messages_list = list(messages.get_messages(request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(str(messages_list[0]), "Step created successfully.")
        self.assertEqual(response.status_code, 302)

    @patch("bots_chain.services.ChainStepService.update_step")
    def test_update_step_success(self, mock_update_step):
        mock_update_step.return_value = {"id": 1, "name": "Updated Step"}

        request = self.factory.post(
            "/", {"name": "Updated Step", "message": "Test message"}
        )
        request.user = self.user
        request = self._add_messages_to_request(request)

        response = UpdateChainStepView.as_view()(
            request, bot_id=self.bot.id, chain_id=1, step_id=1
        )

        messages_list = list(messages.get_messages(request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(str(messages_list[0]), "Step updated successfully.")
        self.assertEqual(response.status_code, 302)

    @patch("bots_chain.services.ChainStepService.delete_step")
    def test_delete_step_success(self, mock_delete_step):
        mock_delete_step.return_value = True

        request = self.factory.post("/")
        request.user = self.user
        request = self._add_messages_to_request(request)

        response = DeleteChainStepView.as_view()(
            request, bot_id=self.bot.id, chain_id=1, step_id=1
        )

        messages_list = list(messages.get_messages(request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(str(messages_list[0]), "Step deleted successfully.")
        self.assertEqual(response.status_code, 302)


class ChainButtonViewsTestCase(BaseChainViewTestCase):
    @patch("bots_chain.services.ChainButtonService.create_button")
    def test_create_button_success(self, mock_create_button):
        mock_create_button.return_value = {"id": 1, "text": "New Button"}

        request = self.factory.post("/", {"step_id": "1"})
        request.user = self.user
        request = self._add_messages_to_request(request)

        response = CreateChainButtonView.as_view()(
            request, bot_id=self.bot.id, chain_id=1
        )

        messages_list = list(messages.get_messages(request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(str(messages_list[0]), "Button created successfully.")
        self.assertEqual(response.status_code, 302)

    @patch("bots_chain.services.ChainButtonService.update_button")
    def test_update_button_success(self, mock_update_button):
        mock_update_button.return_value = {"id": 1, "text": "Updated Button"}

        request = self.factory.post("/", {"text": "Updated Button"})
        request.user = self.user
        request = self._add_messages_to_request(request)

        response = UpdateChainButtonView.as_view()(
            request, bot_id=self.bot.id, chain_id=1, button_id=1
        )

        messages_list = list(messages.get_messages(request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(str(messages_list[0]), "Button updated successfully.")
        self.assertEqual(response.status_code, 302)

    @patch("bots_chain.services.ChainButtonService.delete_button")
    def test_delete_button_success(self, mock_delete_button):
        mock_delete_button.return_value = True

        request = self.factory.post("/")
        request.user = self.user
        request = self._add_messages_to_request(request)

        response = DeleteChainButtonView.as_view()(
            request, bot_id=self.bot.id, chain_id=1, button_id=1
        )

        messages_list = list(messages.get_messages(request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(str(messages_list[0]), "Button deleted successfully.")
        self.assertEqual(response.status_code, 302)


class ChainResultsViewTestCase(BaseChainViewTestCase):
    @patch("bots_chain.services.ChainService.get_chain_results")
    def test_get_results_success(self, mock_get_results):
        mock_get_results.return_value = [{"id": 1, "result": "Test"}]

        request = self.factory.get("/")
        request.user = self.user
        response = ChainResultsView.as_view()(
            request, bot_id=self.bot.id, chain_id=1
        )

        self.assertEqual(response.status_code, 200)
        if hasattr(response, "context_data"):
            self.assertIn("page_obj", response.context_data)
            self.assertEqual(
                len(response.context_data["page_obj"].object_list), 1
            )

    @patch("bots_chain.services.ChainService.get_chain_results")
    def test_get_results_failure(self, mock_get_results):
        mock_get_results.return_value = []

        request = self.factory.get("/")
        request.user = self.user
        response = ChainResultsView.as_view()(
            request, bot_id=self.bot.id, chain_id=1
        )

        self.assertEqual(response.status_code, 200)
        if hasattr(response, "context_data"):
            self.assertEqual(
                len(response.context_data["page_obj"].object_list), 0
            )
