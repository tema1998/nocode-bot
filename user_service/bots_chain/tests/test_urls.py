from bots_chain.views import (
    BotChainDetailView,
    BotChainView,
    ChainResultsView,
    CreateChainButtonView,
    CreateChainStepTextinputView,
    CreateChainStepView,
    CreateChainView,
    DeleteChainButtonView,
    DeleteChainStepView,
    DeleteChainView,
    EditTextinputView,
    UpdateChainButtonView,
    UpdateChainStepView,
    UpdateChainView,
)
from django.test import SimpleTestCase
from django.urls import resolve, reverse


class TestUrls(SimpleTestCase):
    def test_bot_chains_url_resolves(self):
        """Test that the 'bot-chains' URL resolves to the BotChainView view."""
        url = reverse("bot-chains", args=[1])
        self.assertEqual(resolve(url).func.view_class, BotChainView)

    def test_bot_chain_detail_url_resolves(self):
        """Test that the 'bot-chain' URL resolves to the BotChainDetailView view."""
        url = reverse("bot-chain", args=[1, 2])
        self.assertEqual(resolve(url).func.view_class, BotChainDetailView)

    def test_create_chain_url_resolves(self):
        """Test that the 'create-chain' URL resolves to the CreateChainView view."""
        url = reverse("create-chain", args=[1])
        self.assertEqual(resolve(url).func.view_class, CreateChainView)

    def test_update_chain_url_resolves(self):
        """Test that the 'update-chain' URL resolves to the UpdateChainView view."""
        url = reverse("update-chain", args=[1, 2])
        self.assertEqual(resolve(url).func.view_class, UpdateChainView)

    def test_delete_chain_url_resolves(self):
        """Test that the 'delete-chain' URL resolves to the DeleteChainView view."""
        url = reverse("delete-chain", args=[1, 2])
        self.assertEqual(resolve(url).func.view_class, DeleteChainView)

    def test_create_chain_step_url_resolves(self):
        """Test that the 'create-chain-step' URL resolves to the CreateChainStepView view."""
        url = reverse("create-chain-step", args=[1, 2])
        self.assertEqual(resolve(url).func.view_class, CreateChainStepView)

    def test_create_chain_step_textinput_url_resolves(self):
        """Test that the 'create-chain-step-textinput' URL resolves to the CreateChainStepTextinputView view."""
        url = reverse("create-chain-step-textinput", args=[1, 2])
        self.assertEqual(
            resolve(url).func.view_class, CreateChainStepTextinputView
        )

    def test_update_chain_step_url_resolves(self):
        """Test that the 'update-chain-step' URL resolves to the UpdateChainStepView view."""
        url = reverse("update-chain-step", args=[1, 2, 3])
        self.assertEqual(resolve(url).func.view_class, UpdateChainStepView)

    def test_delete_chain_step_url_resolves(self):
        """Test that the 'delete-chain-step' URL resolves to the DeleteChainStepView view."""
        url = reverse("delete-chain-step", args=[1, 2, 3])
        self.assertEqual(resolve(url).func.view_class, DeleteChainStepView)

    def test_edit_text_input_url_resolves(self):
        """Test that the 'edit-text-input' URL resolves to the EditTextinputView view."""
        url = reverse("edit-text-input", args=[1, 2, 3])
        self.assertEqual(resolve(url).func.view_class, EditTextinputView)

    def test_create_chain_button_url_resolves(self):
        """Test that the 'create-chain-button' URL resolves to the CreateChainButtonView view."""
        url = reverse("create-chain-button", args=[1, 2])
        self.assertEqual(resolve(url).func.view_class, CreateChainButtonView)

    def test_update_chain_button_url_resolves(self):
        """Test that the 'update-chain-button' URL resolves to the UpdateChainButtonView view."""
        url = reverse("update-chain-button", args=[1, 2, 3])
        self.assertEqual(resolve(url).func.view_class, UpdateChainButtonView)

    def test_delete_chain_button_url_resolves(self):
        """Test that the 'delete-chain-button' URL resolves to the DeleteChainButtonView view."""
        url = reverse("delete-chain-button", args=[1, 2, 3])
        self.assertEqual(resolve(url).func.view_class, DeleteChainButtonView)

    def test_chain_results_url_resolves(self):
        """Test that the 'chain-results' URL resolves to the ChainResultsView view."""
        url = reverse("chain-results", args=[1, 2])
        self.assertEqual(resolve(url).func.view_class, ChainResultsView)

    def test_url_paths(self):
        """Verify that specific URL paths match the expected patterns."""
        self.assertEqual(
            reverse("bot-chains", args=[1]), "/bots-chain/chains/1/"
        )
        self.assertEqual(
            reverse("bot-chain", args=[1, 2]), "/bots-chain/chain/1/2"
        )
        self.assertEqual(
            reverse("create-chain", args=[1]), "/bots-chain/chain/1"
        )
        self.assertEqual(
            reverse("update-chain", args=[1, 2]),
            "/bots-chain/update-chain/1/2",
        )
        self.assertEqual(
            reverse("delete-chain", args=[1, 2]),
            "/bots-chain/delete-chain/1/2",
        )
        self.assertEqual(
            reverse("create-chain-step", args=[1, 2]),
            "/bots-chain/create-chain-step/1/2",
        )
        self.assertEqual(
            reverse("update-chain-step", args=[1, 2, 3]),
            "/bots-chain/update-chain-step/1/2/3",
        )
        self.assertEqual(
            reverse("chain-results", args=[1, 2]),
            "/bots-chain/chain-results/1/2/",
        )
