from unittest.mock import MagicMock, patch

from bots.models import Bot
from bots_chain.services import (
    ChainButtonService,
    ChainService,
    ChainStepService,
)
from bots_chain.views import *
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory, TestCase
from requests import RequestException


class BaseChainViewTestCase(TestCase):
    def setUp(self):
        """Set up the test case environment for all chain view tests."""
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="testuser", password="12345"
        )
        self.bot = Bot.objects.create(user=self.user, bot_id=123)

    def _add_messages_to_request(self, request):
        """Add a messages storage to the request for testing purposes."""
        setattr(request, "session", "session")  # Mock session attribute
        messages = FallbackStorage(
            request
        )  # Create fallback messaging storage
        setattr(
            request, "_messages", messages
        )  # Attach messages storage to request
        return request


class BotChainViewTestCase(BaseChainViewTestCase):
    @patch("bots_chain.services.ChainService.get_bot_chains")
    def test_get_success(self, mock_get_chains):
        """Test successful retrieval of bot chains."""
        mock_get_chains.return_value = {
            "chains": [{"id": 1, "name": "Test Chain"}]
        }

        request = self.factory.get("/")
        request.user = self.user
        response = BotChainView.as_view()(request, bot_id=self.bot.id)

        self.assertEqual(response.status_code, 200)
        if hasattr(response, "context_data"):
            self.assertIn(
                "chains", response.context_data
            )  # Check if chains are present in context
            self.assertEqual(
                response.context_data["chains"],
                [{"id": 1, "name": "Test Chain"}],
            )

    @patch("bots_chain.services.ChainService.get_bot_chains")
    def test_get_failure(self, mock_get_chains):
        """Test behavior when retrieval of bot chains fails."""
        mock_get_chains.side_effect = RequestException("API error")

        request = self.factory.get("/")
        request.user = self.user
        response = BotChainView.as_view()(request, bot_id=self.bot.id)

        self.assertEqual(response.status_code, 200)
        if hasattr(response, "context_data"):
            self.assertEqual(
                response.context_data["chains"], []
            )  # Ensure chains are empty on failure


class BotChainDetailViewTestCase(BaseChainViewTestCase):
    @patch("bots_chain.services.ChainService.get_chain")
    def test_get_success(self, mock_get_chain):
        """Test successful retrieval of a specific chain's details."""
        chain_data = {"id": 1, "name": "Test Chain"}
        mock_get_chain.return_value = chain_data

        request = self.factory.get("/")
        request.user = self.user
        response = BotChainDetailView.as_view()(
            request, bot_id=self.bot.id, chain_id=1
        )

        self.assertEqual(response.status_code, 200)
        if hasattr(response, "context_data"):
            self.assertEqual(
                response.context_data["chain"], chain_data
            )  # Validate chain data
            self.assertEqual(
                json.loads(response.context_data["chain_json"]), chain_data
            )

    @patch("bots_chain.services.ChainService.get_chain")
    def test_get_failure(self, mock_get_chain):
        """Test behavior when retrieval of a specific chain fails."""
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
            )  # Validate default response on failure
            self.assertEqual(response.context_data["chain_json"], "{}")


class CreateChainViewTestCase(BaseChainViewTestCase):
    @patch("bots_chain.services.ChainService.create_chain")
    def test_post_success(self, mock_create_chain):
        """Test successful creation of a new chain."""
        mock_create_chain.return_value = {"id": 1, "name": "New Chain"}

        request = self.factory.post("/", {"name": "New Chain"})
        request.user = self.user
        request = self._add_messages_to_request(request)

        response = CreateChainView.as_view()(request, bot_id=self.bot.id)

        messages_list = list(
            messages.get_messages(request)
        )  # Retrieve messages from request
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(
            str(messages_list[0]), "Цепочка создана успешно."
        )  # Validate success message
        self.assertEqual(response.status_code, 302)  # Validate redirection
        self.assertEqual(
            response.url, f"/bots-chain/bots/{self.bot.id}/chains/"
        )  # Validate redirect URL

    @patch("bots_chain.services.ChainService.create_chain")
    def test_post_failure(self, mock_create_chain):
        """Test behavior when chain creation fails."""
        mock_create_chain.side_effect = RequestException("API error")

        request = self.factory.post("/", {"name": "New Chain"})
        request.user = self.user
        request = self._add_messages_to_request(request)

        response = CreateChainView.as_view()(request, bot_id=self.bot.id)

        messages_list = list(messages.get_messages(request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(
            str(messages_list[0]),
            "Ошибка создания цепочки. Возможно цепочка с таким именем уже существует.",
        )  # Validate failure message
        self.assertEqual(response.status_code, 302)


class UpdateChainViewTestCase(BaseChainViewTestCase):
    @patch("bots_chain.services.ChainService.update_chain")
    def test_post_success(self, mock_update_chain):
        """Test successful update of an existing chain."""
        mock_update_chain.return_value = {"id": 1, "name": "Updated Chain"}

        request = self.factory.post("/", {"name": "Updated Chain"})
        request.user = self.user
        request = self._add_messages_to_request(request)

        response = UpdateChainView.as_view()(
            request, bot_id=self.bot.id, chain_id=1
        )

        messages_list = list(messages.get_messages(request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(
            str(messages_list[0]), "Цепочка успешно обновлена."
        )  # Validate update success message
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url, f"/bots-chain/bots/{self.bot.id}/chains/1/"
        )  # Validate redirect URL

    @patch("bots_chain.services.ChainService.update_chain")
    def test_post_failure(self, mock_update_chain):
        """Test behavior when chain update fails."""
        mock_update_chain.side_effect = RequestException("API error")

        request = self.factory.post("/", {"name": "Updated Chain"})
        request.user = self.user
        request = self._add_messages_to_request(request)

        response = UpdateChainView.as_view()(
            request, bot_id=self.bot.id, chain_id=1
        )

        messages_list = list(messages.get_messages(request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(
            str(messages_list[0]), "Ошибка обновления цепочки."
        )  # Validate failure message
        self.assertEqual(response.status_code, 302)


class DeleteChainViewTestCase(BaseChainViewTestCase):
    @patch("bots_chain.services.ChainService.delete_chain")
    def test_post_success(self, mock_delete_chain):
        """Test successful deletion of a chain."""
        mock_delete_chain.return_value = True

        request = self.factory.post("/")
        request.user = self.user
        request = self._add_messages_to_request(request)

        response = DeleteChainView.as_view()(
            request, bot_id=self.bot.id, chain_id=1
        )

        messages_list = list(messages.get_messages(request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(
            str(messages_list[0]), "Цепочка успешно удалена."
        )  # Validate deletion success message
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url, f"/bots-chain/bots/{self.bot.id}/chains/"
        )  # Validate redirect URL

    @patch("bots_chain.services.ChainService.delete_chain")
    def test_post_failure(self, mock_delete_chain):
        """Test behavior when deletion of a chain fails."""
        mock_delete_chain.side_effect = RequestException("API error")

        request = self.factory.post("/")
        request.user = self.user
        request = self._add_messages_to_request(request)

        response = DeleteChainView.as_view()(
            request, bot_id=self.bot.id, chain_id=1
        )

        messages_list = list(messages.get_messages(request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(
            str(messages_list[0]), "Ошибка удаления цепочки."
        )  # Validate failure message
        self.assertEqual(response.status_code, 302)


class ChainStepViewsTestCase(BaseChainViewTestCase):
    @patch("bots_chain.services.ChainStepService.create_step")
    def test_create_step_success(self, mock_create_step):
        """Test successful creation of a new chain step."""
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
        self.assertEqual(
            str(messages_list[0]), "Шаг успешно создан."
        )  # Validate creation success message
        self.assertEqual(response.status_code, 302)

    @patch("bots_chain.services.ChainStepService.update_step")
    def test_update_step_success(self, mock_update_step):
        """Test successful update of an existing chain step."""
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
        self.assertEqual(
            str(messages_list[0]), "Шаг успешно обновлен."
        )  # Validate update success message
        self.assertEqual(response.status_code, 302)

    @patch("bots_chain.services.ChainStepService.delete_step")
    def test_delete_step_success(self, mock_delete_step):
        """Test successful deletion of a chain step."""
        mock_delete_step.return_value = True

        request = self.factory.post("/")
        request.user = self.user
        request = self._add_messages_to_request(request)

        response = DeleteChainStepView.as_view()(
            request, bot_id=self.bot.id, chain_id=1, step_id=1
        )

        messages_list = list(messages.get_messages(request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(
            str(messages_list[0]), "Шаг успешно удален."
        )  # Validate deletion success message
        self.assertEqual(response.status_code, 302)


class ChainButtonViewsTestCase(BaseChainViewTestCase):
    @patch("bots_chain.services.ChainButtonService.create_button")
    def test_create_button_success(self, mock_create_button):
        """Test successful creation of a new chain button."""
        mock_create_button.return_value = {"id": 1, "text": "New Button"}

        request = self.factory.post("/", {"step_id": "1"})
        request.user = self.user
        request = self._add_messages_to_request(request)

        response = CreateChainButtonView.as_view()(
            request, bot_id=self.bot.id, chain_id=1
        )

        messages_list = list(messages.get_messages(request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(
            str(messages_list[0]), "Кнопка успешно создана."
        )  # Validate creation success message
        self.assertEqual(response.status_code, 302)

    @patch("bots_chain.services.ChainButtonService.update_button")
    def test_update_button_success(self, mock_update_button):
        """Test successful update of an existing chain button."""
        mock_update_button.return_value = {"id": 1, "text": "Updated Button"}

        request = self.factory.post("/", {"text": "Updated Button"})
        request.user = self.user
        request = self._add_messages_to_request(request)

        response = UpdateChainButtonView.as_view()(
            request, bot_id=self.bot.id, chain_id=1, button_id=1
        )

        messages_list = list(messages.get_messages(request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(
            str(messages_list[0]), "Кнопка успешно обновлена."
        )  # Validate update success message
        self.assertEqual(response.status_code, 302)

    @patch("bots_chain.services.ChainButtonService.delete_button")
    def test_delete_button_success(self, mock_delete_button):
        """Test successful deletion of a chain button."""
        mock_delete_button.return_value = True

        request = self.factory.post("/")
        request.user = self.user
        request = self._add_messages_to_request(request)

        response = DeleteChainButtonView.as_view()(
            request, bot_id=self.bot.id, chain_id=1, button_id=1
        )

        messages_list = list(messages.get_messages(request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(
            str(messages_list[0]), "Кнопка успешно удалена."
        )  # Validate deletion success message
        self.assertEqual(response.status_code, 302)


class ChainResultsViewTestCase(BaseChainViewTestCase):
    @patch("bots_chain.services.ChainService.get_chain_results")
    def test_get_results_success(self, mock_get_results):
        """Test successful retrieval of chain results."""
        mock_get_results.return_value = [{"id": 1, "result": "Test"}]

        request = self.factory.get("/")
        request.user = self.user
        response = ChainResultsView.as_view()(
            request, bot_id=self.bot.id, chain_id=1
        )

        self.assertEqual(response.status_code, 200)
        if hasattr(response, "context_data"):
            self.assertIn(
                "page_obj", response.context_data
            )  # Validate presence of pagination object
            self.assertEqual(
                len(response.context_data["page_obj"].object_list), 1
            )  # Validate number of results

    @patch("bots_chain.services.ChainService.get_chain_results")
    def test_get_results_failure(self, mock_get_results):
        """Test behavior when retrieval of chain results fails."""
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
            )  # Ensure that no results are returned
