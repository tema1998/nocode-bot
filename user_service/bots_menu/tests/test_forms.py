import re

from bots_menu.forms import (
    BotDefaultReplyForm,
    BotForm,
    BotMainMenuButtonForm,
    BotMainMenuForm,
)
from django import forms
from django.test import TestCase


class BotFormTest(TestCase):
    def test_form_fields(self):
        """Test that the BotForm contains the expected fields."""
        form = BotForm()
        self.assertIn(
            "token", form.fields
        )  # Check if 'token' field is present
        self.assertIsInstance(
            form.fields["token"], forms.CharField
        )  # Ensure it is a CharField

    def test_token_field_attributes(self):
        """Test attributes of the 'token' field in the BotForm."""
        form = BotForm()
        field = form.fields["token"]
        self.assertEqual(
            field.label, "Token телеграм бота"
        )  # Check field label
        self.assertEqual(field.max_length, 255)  # Check maximum length
        self.assertEqual(
            field.widget.attrs["class"], "form-control form-control-user"
        )  # Check CSS class
        self.assertEqual(
            field.widget.attrs["placeholder"],
            "1234567890:QWERTYUIOPasdfghjklZXCVBNMqwertyuio",  # Check placeholder text
        )

    def test_token_validation(self):
        """Test validation behavior for the 'token' field with valid and invalid tokens."""
        # Valid tokens
        valid_tokens = [
            "123456789:ABCdefGHIJKlmNoPQRstuVWXyz",
            "987654321:asdfghjklqwertyuiopzxcvbnm",
            "111111111:AAAAAAAAAAAAAAAAAAAAAAAAAA",
            "123:abc",
        ]

        # Invalid tokens
        invalid_tokens = [
            "123456789",  # Missing the token part after the colon
            ":ABCdefGHIJKlmNoPQRstuVWXyz",  # Missing the bot ID part
            "abc:123",  # Invalid format
            "123456789:ABC def",  # Contains a space
            "123456789:ABC!def",  # Contains special character
        ]

        # Validate the valid tokens
        for token in valid_tokens:
            with self.subTest(token=token):
                form = BotForm(data={"token": token})
                self.assertTrue(form.is_valid())  # Should pass validation

        # Validate the invalid tokens
        for token in invalid_tokens:
            with self.subTest(token=token):
                form = BotForm(data={"token": token})
                self.assertFalse(form.is_valid())  # Should fail validation
                self.assertIn(
                    "token", form.errors
                )  # Check if there is an error for 'token'


class BotDefaultReplyFormTest(TestCase):
    def test_form_fields(self):
        """Test that the BotDefaultReplyForm contains the expected fields."""
        form = BotDefaultReplyForm()
        self.assertIn(
            "default_reply", form.fields
        )  # Check if 'default_reply' field is present
        self.assertIsInstance(
            form.fields["default_reply"], forms.CharField
        )  # Ensure it is a CharField

    def test_field_attributes(self):
        """Test attributes of the 'default_reply' field in the BotDefaultReplyForm."""
        field = BotDefaultReplyForm().fields["default_reply"]
        self.assertEqual(
            field.label,
            "Ответ бота на неизвестную команду/сообщение:",  # Check field label
        )
        self.assertEqual(field.max_length, 3000)  # Check maximum length
        self.assertEqual(
            field.widget.attrs["class"],
            "form-control form-control-user",  # Check CSS class
        )

    def test_validation(self):
        """Test validation behavior for the 'default_reply' field."""
        # Valid case
        valid_data = {"default_reply": "Стандартный ответ"}  # Valid reply text
        form = BotDefaultReplyForm(data=valid_data)
        self.assertTrue(form.is_valid())  # Should pass validation

        # Invalid cases
        invalid_data = [
            {"default_reply": ""},
            {"default_reply": "x" * 3001},
        ]  # Empty and overly long replies

        for data in invalid_data:
            with self.subTest(data=data):
                form = BotDefaultReplyForm(data=data)
                self.assertFalse(form.is_valid())  # Should fail validation


class BotMainMenuFormTest(TestCase):
    def test_form_fields(self):
        """Test that the BotMainMenuForm contains the expected fields."""
        form = BotMainMenuForm()
        self.assertIn(
            "welcome_message", form.fields
        )  # Check if 'welcome_message' field is present
        self.assertIsInstance(
            form.fields["welcome_message"], forms.CharField
        )  # Ensure it is a CharField

    def test_field_attributes(self):
        """Test attributes of the 'welcome_message' field in the BotMainMenuForm."""
        field = BotMainMenuForm().fields["welcome_message"]
        self.assertEqual(
            field.label, "Приветственное сообщение:"
        )  # Check field label
        self.assertEqual(field.max_length, 3000)  # Check maximum length
        self.assertEqual(
            field.widget.attrs["class"],
            "form-control form-control-user",  # Check CSS class
        )

    def test_validation(self):
        """Test validation behavior for the 'welcome_message' field."""
        # Valid case
        valid_data = {
            "welcome_message": "Добро пожаловать!"
        }  # Valid welcome message
        form = BotMainMenuForm(data=valid_data)
        self.assertTrue(form.is_valid())  # Should pass validation

        # Invalid cases
        invalid_data = [
            {"welcome_message": "x" * 3001},  # Too long welcome message
        ]

        for data in invalid_data:
            with self.subTest(data=data):
                form = BotMainMenuForm(data=data)
                self.assertFalse(form.is_valid())  # Should fail validation


class BotMainMenuButtonFormTest(TestCase):
    def test_form_fields(self):
        """Test that the BotMainMenuButtonForm contains the expected fields."""
        form = BotMainMenuButtonForm()
        fields = form.fields
        self.assertCountEqual(
            fields.keys(),
            [
                "button_text",
                "reply_text",
                "chain_id",
            ],  # Check the expected fields
        )
        self.assertIsInstance(
            fields["button_text"], forms.CharField
        )  # Ensure 'button_text' is a CharField
        self.assertIsInstance(
            fields["reply_text"], forms.CharField
        )  # Ensure 'reply_text' is a CharField
        self.assertIsInstance(
            fields["chain_id"], forms.IntegerField
        )  # Ensure 'chain_id' is an IntegerField

    def test_field_attributes(self):
        """Test attributes of fields in the BotMainMenuButtonForm."""
        form = BotMainMenuButtonForm()

        # Button text
        btn_field = form.fields["button_text"]
        self.assertEqual(btn_field.label, "Текст кнопки:")  # Check label
        self.assertEqual(btn_field.max_length, 64)  # Check maximum length
        self.assertEqual(
            btn_field.widget.attrs["class"],
            "form-control form-control-user",  # Check CSS class
        )

        # Reply text
        reply_field = form.fields["reply_text"]
        self.assertEqual(
            reply_field.label, "Текст ответного сообщения:"
        )  # Check label
        self.assertEqual(reply_field.max_length, 3000)  # Check maximum length
        self.assertEqual(
            reply_field.widget.attrs["class"],
            "form-control form-control-user",  # Check CSS class
        )

        # Chain ID (should have no widget attrs)
        chain_field = form.fields["chain_id"]
        self.assertEqual(
            chain_field.widget.attrs, {}
        )  # Check that chain_id has no attributes

    def test_validation(self):
        """Test validation behavior for the BotMainMenuButtonForm fields."""
        # Valid case
        valid_data = {
            "button_text": "Кнопка",  # Valid button text
            "reply_text": "Ответ",  # Valid reply text
            "chain_id": 1,  # Valid chain ID
        }
        form = BotMainMenuButtonForm(data=valid_data)
        self.assertTrue(form.is_valid())  # Should pass validation

        # Invalid cases
        invalid_cases = [
            {
                "button_text": "",
                "reply_text": "Ответ",
                "chain_id": 1,
            },  # Empty button text
            {
                "button_text": "Кнопка",
                "reply_text": "",
                "chain_id": 1,
            },  # Empty reply text
            {
                "button_text": "Кнопка",
                "reply_text": "Ответ",
                "chain_id": "",
            },  # Empty chain ID
            {
                "button_text": "x" * 65,
                "reply_text": "Ответ",
                "chain_id": 1,
            },  # Too long button text
            {
                "button_text": "Кнопка",
                "reply_text": "x" * 3001,
                "chain_id": 1,
            },  # Too long reply text
        ]

        for data in invalid_cases:
            with self.subTest(data=data):
                form = BotMainMenuButtonForm(data=data)
                self.assertFalse(form.is_valid())  # Should fail validation
