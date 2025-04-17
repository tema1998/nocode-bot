from bots_mailing.views import MailingView
from django.test import SimpleTestCase
from django.urls import resolve, reverse


class TestMailingUrl(SimpleTestCase):
    def test_mailing_url_resolves(self):
        # Test URL resolution
        url = reverse("mailing", args=[1])
        self.assertEqual(resolve(url).func.view_class, MailingView)

    def test_mailing_url_pattern(self):
        # Test URL pattern
        self.assertEqual(
            reverse("mailing", args=[5]), "/bots-mailing/bots/5/mailing/"
        )

    def test_mailing_url_with_different_ids(self):
        # Test with different bot IDs
        test_cases = [
            (1, "/bots-mailing/bots/1/mailing/"),
            (42, "/bots-mailing/bots/42/mailing/"),
            (999, "/bots-mailing/bots/999/mailing/"),
        ]

        for bot_id, expected_url in test_cases:
            with self.subTest(bot_id=bot_id):
                self.assertEqual(
                    reverse("mailing", args=[bot_id]), expected_url
                )
