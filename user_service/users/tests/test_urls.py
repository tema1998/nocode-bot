from django.test import SimpleTestCase
from django.urls import resolve, reverse
from users.views import LoginView, LogoutView, RegisterView


class TestAuthUrls(SimpleTestCase):
    def test_register_url_resolves(self):
        url = reverse("register")
        self.assertEqual(resolve(url).func.view_class, RegisterView)
        self.assertEqual(url, "/auth/register/")

    def test_login_url_resolves(self):
        url = reverse("login")
        self.assertEqual(resolve(url).func.view_class, LoginView)
        self.assertEqual(url, "/auth/login/")

    def test_logout_url_resolves(self):
        url = reverse("logout")
        self.assertEqual(resolve(url).func.view_class, LogoutView)
        self.assertEqual(url, "/auth/logout/")

    def test_url_patterns(self):
        test_cases = [
            ("register", [], "/auth/register/"),
            ("login", [], "/auth/login/"),
            ("logout", [], "/auth/logout/"),
        ]

        for name, args, expected_url in test_cases:
            with self.subTest(name=name):
                self.assertEqual(reverse(name, args=args), expected_url)
