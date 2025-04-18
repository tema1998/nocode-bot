from django.test import SimpleTestCase
from django.urls import resolve, reverse
from users.views import LoginView, LogoutView, RegisterView


class TestAuthUrls(SimpleTestCase):
    """Test suite for authentication URLs."""

    def test_register_url_resolves(self):
        """Test that the register URL resolves to the RegisterView."""
        url = reverse("register")
        self.assertEqual(
            resolve(url).func.view_class,
            RegisterView,
            msg="Register URL should resolve to RegisterView.",
        )
        self.assertEqual(
            url,
            "/auth/register/",
            msg="Register URL does not match the expected pattern.",
        )

    def test_login_url_resolves(self):
        """Test that the login URL resolves to the LoginView."""
        url = reverse("login")
        self.assertEqual(
            resolve(url).func.view_class,
            LoginView,
            msg="Login URL should resolve to LoginView.",
        )
        self.assertEqual(
            url,
            "/auth/login/",
            msg="Login URL does not match the expected pattern.",
        )

    def test_logout_url_resolves(self):
        """Test that the logout URL resolves to the LogoutView."""
        url = reverse("logout")
        self.assertEqual(
            resolve(url).func.view_class,
            LogoutView,
            msg="Logout URL should resolve to LogoutView.",
        )
        self.assertEqual(
            url,
            "/auth/logout/",
            msg="Logout URL does not match the expected pattern.",
        )

    def test_url_patterns(self):
        """Test URL patterns for authentication."""
        test_cases = [
            ("register", [], "/auth/register/"),
            ("login", [], "/auth/login/"),
            ("logout", [], "/auth/logout/"),
        ]

        for name, args, expected_url in test_cases:
            with self.subTest(name=name):
                self.assertEqual(
                    reverse(name, args=args),
                    expected_url,
                    msg=f"URL reverse for {name} does not match expected.",
                )
