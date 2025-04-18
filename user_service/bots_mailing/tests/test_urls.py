from bots_mailing.views import MailingView
from django.test import SimpleTestCase
from django.urls import resolve, reverse


class TestMailingUrl(SimpleTestCase):
    def test_mailing_url_resolves(self):
        """Test that the URL for mailing resolves to the MailingView."""
        url = reverse(
            "mailing", args=[1]
        )  # Generate the URL for a bot with ID 1
        self.assertEqual(
            resolve(url).func.view_class, MailingView
        )  # Check if it resolves to MailingView

    def test_mailing_url_pattern(self):
        """Test the URL pattern for the mailing view."""
        self.assertEqual(
            reverse("mailing", args=[5]), "/bots-mailing/bots/5/mailing/"
        )  # Ensure the URL is correctly formatted for bot ID 5

    def test_mailing_url_with_different_ids(self):
        """Test URL generation with different bot IDs."""
        # Define a list of test cases with bot IDs and the expected URLs
        test_cases = [
            (1, "/bots-mailing/bots/1/mailing/"),
            (42, "/bots-mailing/bots/42/mailing/"),
            (999, "/bots-mailing/bots/999/mailing/"),
        ]

        for bot_id, expected_url in test_cases:
            with self.subTest(
                bot_id=bot_id
            ):  # Create a sub-test for each bot ID
                self.assertEqual(
                    reverse("mailing", args=[bot_id]), expected_url
                )  # Check that the generated URL matches the expected URL for each bot ID
