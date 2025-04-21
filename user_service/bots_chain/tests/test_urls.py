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
        """Test that the 'chain-list' URL resolves to the BotChainView view."""
        url = reverse("chain-list", args=[1])
        self.assertEqual(resolve(url).func.view_class, BotChainView)

    def test_bot_chain_detail_url_resolves(self):
        """Test that the 'chain-detail' URL resolves to the BotChainDetailView view."""
        url = reverse("chain-detail", args=[1, 2])
        self.assertEqual(resolve(url).func.view_class, BotChainDetailView)

    def test_create_chain_url_resolves(self):
        """Test that the 'chain-create' URL resolves to the CreateChainView view."""
        url = reverse("chain-create", args=[1])
        self.assertEqual(resolve(url).func.view_class, CreateChainView)

    def test_update_chain_url_resolves(self):
        """Test that the 'chain-update' URL resolves to the UpdateChainView view."""
        url = reverse("chain-update", args=[1, 2])
        self.assertEqual(resolve(url).func.view_class, UpdateChainView)

    def test_delete_chain_url_resolves(self):
        """Test that the 'chain-delete' URL resolves to the DeleteChainView view."""
        url = reverse("chain-delete", args=[1, 2])
        self.assertEqual(resolve(url).func.view_class, DeleteChainView)

    def test_create_chain_step_url_resolves(self):
        """Test that the 'step-create' URL resolves to the CreateChainStepView view."""
        url = reverse("step-create", args=[1, 2])
        self.assertEqual(resolve(url).func.view_class, CreateChainStepView)

    def test_step_create_text_url_resolves(self):
        """Test that the 'step-create-text' URL resolves to the CreateChainStepTextinputView view."""
        url = reverse("step-create-text", args=[1, 2])
        self.assertEqual(
            resolve(url).func.view_class, CreateChainStepTextinputView
        )

    def test_update_chain_step_url_resolves(self):
        """Test that the 'step-detail' URL resolves to the UpdateChainStepView view."""
        url = reverse("step-detail", args=[1, 2, 3])
        self.assertEqual(resolve(url).func.view_class, UpdateChainStepView)

    def test_delete_chain_step_url_resolves(self):
        """Test that the 'delete-chain-step' URL resolves to the DeleteChainStepView view."""
        url = reverse("step-delete", args=[1, 2, 3])
        self.assertEqual(resolve(url).func.view_class, DeleteChainStepView)

    def test_edit_text_input_url_resolves(self):
        """Test that the 'step-edit-text-input' URL resolves to the EditTextinputView view."""
        url = reverse("step-edit-text-input", args=[1, 2, 3])
        self.assertEqual(resolve(url).func.view_class, EditTextinputView)

    def test_create_chain_button_url_resolves(self):
        """Test that the 'button-create' URL resolves to the CreateChainButtonView view."""
        url = reverse("button-create", args=[1, 2])
        self.assertEqual(resolve(url).func.view_class, CreateChainButtonView)

    def test_update_chain_button_url_resolves(self):
        """Test that the 'button-detail' URL resolves to the UpdateChainButtonView view."""
        url = reverse("button-detail", args=[1, 2, 3])
        self.assertEqual(resolve(url).func.view_class, UpdateChainButtonView)

    def test_delete_chain_button_url_resolves(self):
        """Test that the 'button-delete' URL resolves to the DeleteChainButtonView view."""
        url = reverse("button-delete", args=[1, 2, 3])
        self.assertEqual(resolve(url).func.view_class, DeleteChainButtonView)

    def test_chain_results_url_resolves(self):
        """Test that the 'chain-results' URL resolves to the ChainResultsView view."""
        url = reverse("chain-results", args=[1, 2])
        self.assertEqual(resolve(url).func.view_class, ChainResultsView)

    def test_url_paths(self):
        """Verify that specific URL paths match the expected patterns."""
        self.assertEqual(
            reverse("chain-list", args=[1]), "/bots-chain/bots/1/chains/"
        )
        self.assertEqual(
            reverse("chain-detail", args=[1, 2]),
            "/bots-chain/bots/1/chains/2/",
        )
        self.assertEqual(
            reverse("chain-create", args=[1]),
            "/bots-chain/bots/1/chains/create/",
        )
        self.assertEqual(
            reverse("chain-update", args=[1, 2]),
            "/bots-chain/bots/1/chains/2/update/",
        )
        self.assertEqual(
            reverse("chain-delete", args=[1, 2]),
            "/bots-chain/bots/1/chains/2/delete/",
        )
        self.assertEqual(
            reverse("step-create", args=[1, 2]),
            "/bots-chain/bots/1/chains/2/steps/create/",
        )
        self.assertEqual(
            reverse("step-detail", args=[1, 2, 3]),
            "/bots-chain/bots/1/chains/2/steps/3/",
        )
        self.assertEqual(
            reverse("step-delete", args=[1, 2, 3]),
            "/bots-chain/bots/1/chains/2/steps/3/delete/",
        )
