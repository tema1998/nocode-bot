from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.test import TestCase
from users.forms import LoginForm, RegisterForm


class RegisterFormTest(TestCase):
    """Test suite for the RegisterForm class."""

    def test_form_meta(self):
        """Check the form's model and fields."""
        self.assertEqual(RegisterForm.Meta.model, User)
        self.assertEqual(
            RegisterForm.Meta.fields,
            ["username", "email", "password1", "password2"],
        )

    def test_email_field(self):
        """Test the email field properties."""
        form = RegisterForm()
        email_field = form.fields["email"]
        self.assertTrue(
            email_field.required, msg="Email field should be required."
        )
        self.assertIsInstance(
            email_field,
            forms.EmailField,
            msg="Email field should be an instance of EmailField.",
        )
        self.assertEqual(
            email_field.widget.attrs["class"], "form-control form-control-user"
        )
        self.assertEqual(
            email_field.widget.attrs["placeholder"], "Ваш Email адрес"
        )

    def test_field_widget_attrs(self):
        """Check widget attributes for fields."""
        form = RegisterForm()
        fields_to_check = {
            "username": {
                "class": "form-control form-control-user",
                "placeholder": "Ваш логин",
            },
            "password1": {
                "class": "form-control form-control-user",
                "placeholder": "Ваш пароль",
            },
            "password2": {
                "class": "form-control form-control-user",
                "placeholder": "Повторите ваш пароль",
            },
        }

        for field_name, expected_attrs in fields_to_check.items():
            with self.subTest(field=field_name):
                widget = form.fields[field_name].widget
                for attr, value in expected_attrs.items():
                    self.assertEqual(widget.attrs[attr], value)

    def test_form_validation(self):
        """Check that the form validates correctly with valid and invalid data."""
        valid_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password1": "ComplexPass123!",
            "password2": "ComplexPass123!",
        }
        form = RegisterForm(data=valid_data)
        self.assertTrue(
            form.is_valid(), msg="Form should be valid with proper data."
        )

        invalid_cases = [
            {
                "username": "testuser",
                "email": "test@example.com",
                "password1": "ComplexPass123!",
                "password2": "DifferentPass123!",
            },
            {
                "username": "testuser",
                "email": "not-an-email",
                "password1": "ComplexPass123!",
                "password2": "ComplexPass123!",
            },
            {
                "username": "",
                "email": "test@example.com",
                "password1": "ComplexPass123!",
                "password2": "ComplexPass123!",
            },
        ]

        for case in invalid_cases:
            with self.subTest(case=case):
                form = RegisterForm(data=case)
                self.assertFalse(
                    form.is_valid(),
                    msg=f"Form should be invalid for case: {case}",
                )

    def test_error_class_adding(self):
        """Test addition of the 'is-invalid' class on errors."""
        invalid_data = {
            "username": "",
            "email": "test@example.com",
            "password1": "ComplexPass123!",
            "password2": "ComplexPass123!",
        }
        form = RegisterForm(data=invalid_data)
        form.is_valid()  # Process validation

        self.assertIn(
            "is-invalid",
            form.fields["username"].widget.attrs["class"],
            msg="Username field should have 'is-invalid' class.",
        )
        self.assertNotIn(
            "is-invalid",
            form.fields["email"].widget.attrs["class"],
            msg="Email field should not have 'is-invalid' class.",
        )


class LoginFormTest(TestCase):
    """Test suite for the LoginForm class."""

    def test_form_inheritance(self):
        """Check that LoginForm inherits from AuthenticationForm."""
        self.assertTrue(issubclass(LoginForm, AuthenticationForm))

    def test_field_widget_attrs(self):
        """Check widget attributes for login fields."""
        form = LoginForm()
        fields_to_check = {
            "username": {
                "class": "form-control form-control-user",
                "placeholder": "Ваш логин",
            },
            "password": {
                "class": "form-control form-control-user",
                "placeholder": "Ваш пароль",
            },
        }

        for field_name, expected_attrs in fields_to_check.items():
            with self.subTest(field=field_name):
                widget = form.fields[field_name].widget
                for attr, value in expected_attrs.items():
                    self.assertEqual(widget.attrs[attr], value)

    def test_error_class_adding(self):
        """Test addition of the 'is-invalid' class on errors."""
        invalid_data = {"username": "", "password": ""}
        form = LoginForm(data=invalid_data)
        form.is_valid()

        self.assertIn(
            "is-invalid",
            form.fields["username"].widget.attrs["class"],
            msg="Username field should have 'is-invalid' class.",
        )
        self.assertIn(
            "is-invalid",
            form.fields["password"].widget.attrs["class"],
            msg="Password field should have 'is-invalid' class.",
        )
