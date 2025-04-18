from bots.forms import BotDefaultReplyForm, BotForm
from django import forms
from django.test import TestCase


class BotFormTest(TestCase):
    def test_form_fields(self):
        """Verify that the BotForm contains the expected fields."""
        form = BotForm()
        self.assertIn("token", form.fields)  # Check if 'token' field exists
        self.assertIsInstance(
            form.fields["token"], forms.CharField
        )  # Ensure 'token' is a CharField

    def test_token_field_attributes(self):
        """Verify the attributes of the 'token' field."""
        form = BotForm()
        field = form.fields["token"]
        self.assertEqual(
            field.label, "Token телеграм бота"
        )  # Check the label of the field
        self.assertEqual(
            field.max_length, 255
        )  # Ensure the max length is set correctly
        self.assertEqual(
            field.widget.attrs["class"],
            "form-control form-control-user",  # Check the CSS class
        )
        self.assertIn(
            "placeholder", field.widget.attrs
        )  # Ensure placeholder is present

    def test_token_validation(self):
        """Test the validation logic for the token field."""
        # Valid token formats to test
        valid_tokens = [
            "123456789:ABCdefGHIJKlmNoPQRstuVWXyz",
            "987654321:asdfghjklqwertyuiopzxcvbnm",
            "111111111:AAAAAAAAAAAAAAAAAAAAAAAAAA",
            "123:abc",
        ]

        # Invalid token formats to test
        invalid_tokens = [
            "123456789",  # Missing colon
            ":ABCdefGHIJKlmNoPQRstuVWXyz",  # Missing digits
            "abc:123",  # Digits after the colon
            "123456789:ABC def",  # Contains whitespace
            "123456789:ABC!def",  # Contains special character
        ]

        # Validate the valid tokens
        for token in valid_tokens:
            with self.subTest(
                token=token
            ):  # Create a subtest for better reporting
                form = BotForm(
                    data={"token": token}
                )  # Create a form instance with valid token
                self.assertTrue(
                    form.is_valid()
                )  # Check that the form is valid
                self.assertEqual(
                    form.cleaned_data["token"], token
                )  # Ensure cleaned data matches input

        # Validate the invalid tokens
        for token in invalid_tokens:
            with self.subTest(
                token=token
            ):  # Create a subtest for better reporting
                form = BotForm(
                    data={"token": token}
                )  # Create a form instance with invalid token
                self.assertFalse(
                    form.is_valid()
                )  # Check that the form is invalid
                self.assertIn(
                    "token", form.errors
                )  # Ensure there is an error for the 'token' field
                self.assertEqual(
                    form.errors["token"][0],
                    "Неверный формат токена Telegram, пример токена: '123456789:ABCdefGHIJKlmNoPQRstuVWXyz'.",  # Check the specific error message
                )


class BotDefaultReplyFormTest(TestCase):
    def test_form_fields(self):
        """Verify that the BotDefaultReplyForm contains the expected fields."""
        form = BotDefaultReplyForm()
        self.assertIn(
            "default_reply", form.fields
        )  # Check if 'default_reply' field exists
        self.assertIsInstance(
            form.fields["default_reply"], forms.CharField
        )  # Ensure 'default_reply' is a CharField

    def test_default_reply_field_attributes(self):
        """Verify the attributes of the 'default_reply' field."""
        form = BotDefaultReplyForm()
        field = form.fields["default_reply"]
        self.assertEqual(
            field.label, "Ответ бота на неизвестную команду/сообщение:"
        )  # Check the label of the field
        self.assertEqual(
            field.max_length, 3000
        )  # Ensure the max length is set correctly
        self.assertEqual(
            field.widget.attrs["class"],
            "form-control form-control-user",  # Check the CSS class
        )

    def test_default_reply_validation(self):
        """Test the validation logic for the default reply field."""
        # Valid data for the default reply field
        valid_data = {"default_reply": "Стандартный ответ бота"}
        form = BotDefaultReplyForm(data=valid_data)
        self.assertTrue(form.is_valid())  # Check that the form is valid
        self.assertEqual(
            form.cleaned_data["default_reply"],
            valid_data["default_reply"],  # Ensure cleaned data matches input
        )

        # Test for overly long data
        long_data = {
            "default_reply": "x" * 3001
        }  # Input longer than the maximum allowed length
        form = BotDefaultReplyForm(data=long_data)
        self.assertFalse(form.is_valid())  # Check that the form is invalid
        self.assertIn(
            "default_reply", form.errors
        )  # Ensure there is an error for the 'default_reply' field
