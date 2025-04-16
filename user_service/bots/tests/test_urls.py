from bots.views import (
    AddBotView,
    BotDefaultReplyView,
    BotDeleteView,
    BotDetailView,
    BotsView,
    BotUsersView,
)
from django.test import SimpleTestCase
from django.urls import resolve, reverse


class TestUrls(SimpleTestCase):
    def test_bots_list_url_resolves(self):
        url = reverse("bots")
        self.assertEqual(resolve(url).func.view_class, BotsView)
        self.assertEqual(url, "/bots/")

    def test_add_bot_url_resolves(self):
        url = reverse("add-bot")
        self.assertEqual(resolve(url).func.view_class, AddBotView)
        self.assertEqual(url, "/bots/add-bot")

    def test_bot_details_url_resolves(self):
        url = reverse("bot-details", args=[1])
        self.assertEqual(resolve(url).func.view_class, BotDetailView)
        self.assertEqual(url, "/bots/1")

    def test_bot_delete_url_resolves(self):
        url = reverse("bot-delete", args=[1])
        self.assertEqual(resolve(url).func.view_class, BotDeleteView)
        self.assertEqual(url, "/bots/delete/1")

    def test_bot_default_reply_url_resolves(self):
        url = reverse("bot-default-reply", args=[1])
        self.assertEqual(resolve(url).func.view_class, BotDefaultReplyView)
        self.assertEqual(url, "/bots/default-reply/1")

    def test_bot_users_url_resolves(self):
        url = reverse("bot-users", args=[1])
        self.assertEqual(resolve(url).func.view_class, BotUsersView)
        self.assertEqual(url, "/bots/bots/1/users/")

    def test_url_patterns(self):
        self.assertEqual(reverse("bots"), "/bots/")
        self.assertEqual(reverse("add-bot"), "/bots/add-bot")
        self.assertEqual(reverse("bot-details", args=[5]), "/bots/5")
        self.assertEqual(reverse("bot-delete", args=[10]), "/bots/delete/10")
        self.assertEqual(
            reverse("bot-default-reply", args=[7]), "/bots/default-reply/7"
        )
        self.assertEqual(reverse("bot-users", args=[3]), "/bots/bots/3/users/")
