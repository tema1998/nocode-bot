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
        url = reverse("bot-chains", args=[1])
        self.assertEqual(resolve(url).func.view_class, BotChainView)

    def test_bot_chain_detail_url_resolves(self):
        url = reverse("bot-chain", args=[1, 2])
        self.assertEqual(resolve(url).func.view_class, BotChainDetailView)

    def test_create_chain_url_resolves(self):
        url = reverse("create-chain", args=[1])
        self.assertEqual(resolve(url).func.view_class, CreateChainView)

    def test_update_chain_url_resolves(self):
        url = reverse("update-chain", args=[1, 2])
        self.assertEqual(resolve(url).func.view_class, UpdateChainView)

    def test_delete_chain_url_resolves(self):
        url = reverse("delete-chain", args=[1, 2])
        self.assertEqual(resolve(url).func.view_class, DeleteChainView)

    def test_create_chain_step_url_resolves(self):
        url = reverse("create-chain-step", args=[1, 2])
        self.assertEqual(resolve(url).func.view_class, CreateChainStepView)

    def test_create_chain_step_textinput_url_resolves(self):
        url = reverse("create-chain-step-textinput", args=[1, 2])
        self.assertEqual(
            resolve(url).func.view_class, CreateChainStepTextinputView
        )

    def test_update_chain_step_url_resolves(self):
        url = reverse("update-chain-step", args=[1, 2, 3])
        self.assertEqual(resolve(url).func.view_class, UpdateChainStepView)

    def test_delete_chain_step_url_resolves(self):
        url = reverse("delete-chain-step", args=[1, 2, 3])
        self.assertEqual(resolve(url).func.view_class, DeleteChainStepView)

    def test_edit_text_input_url_resolves(self):
        url = reverse("edit-text-input", args=[1, 2, 3])
        self.assertEqual(resolve(url).func.view_class, EditTextinputView)

    def test_create_chain_button_url_resolves(self):
        url = reverse("create-chain-button", args=[1, 2])
        self.assertEqual(resolve(url).func.view_class, CreateChainButtonView)

    def test_update_chain_button_url_resolves(self):
        url = reverse("update-chain-button", args=[1, 2, 3])
        self.assertEqual(resolve(url).func.view_class, UpdateChainButtonView)

    def test_delete_chain_button_url_resolves(self):
        url = reverse("delete-chain-button", args=[1, 2, 3])
        self.assertEqual(resolve(url).func.view_class, DeleteChainButtonView)

    def test_chain_results_url_resolves(self):
        url = reverse("chain-results", args=[1, 2])
        self.assertEqual(resolve(url).func.view_class, ChainResultsView)

    def test_url_paths(self):
        # Test some specific URL paths to ensure they match
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
