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
        form = BotForm()
        self.assertIn("token", form.fields)
        self.assertIsInstance(form.fields["token"], forms.CharField)

    def test_token_field_attributes(self):
        form = BotForm()
        field = form.fields["token"]
        self.assertEqual(field.label, "Token телеграм бота")
        self.assertEqual(field.max_length, 255)
        self.assertEqual(
            field.widget.attrs["class"], "form-control form-control-user"
        )
        self.assertEqual(
            field.widget.attrs["placeholder"],
            "1234567890:QWERTYUIOPasdfghjklZXCVBNMqwertyuio",
        )

    def test_token_validation(self):
        # Valid tokens
        valid_tokens = [
            "123456789:ABCdefGHIJKlmNoPQRstuVWXyz",
            "987654321:asdfghjklqwertyuiopzxcvbnm",
            "111111111:AAAAAAAAAAAAAAAAAAAAAAAAAA",
            "123:abc",
        ]

        # Invalid tokens
        invalid_tokens = [
            "123456789",
            ":ABCdefGHIJKlmNoPQRstuVWXyz",
            "abc:123",
            "123456789:ABC def",
            "123456789:ABC!def",
        ]

        for token in valid_tokens:
            with self.subTest(token=token):
                form = BotForm(data={"token": token})
                self.assertTrue(form.is_valid())

        for token in invalid_tokens:
            with self.subTest(token=token):
                form = BotForm(data={"token": token})
                self.assertFalse(form.is_valid())
                self.assertIn("token", form.errors)


class BotDefaultReplyFormTest(TestCase):
    def test_form_fields(self):
        form = BotDefaultReplyForm()
        self.assertIn("default_reply", form.fields)
        self.assertIsInstance(form.fields["default_reply"], forms.CharField)

    def test_field_attributes(self):
        field = BotDefaultReplyForm().fields["default_reply"]
        self.assertEqual(
            field.label, "Ответ бота на неизвестную команду/сообщение:"
        )
        self.assertEqual(field.max_length, 3000)
        self.assertEqual(
            field.widget.attrs["class"], "form-control form-control-user"
        )

    def test_validation(self):
        # Valid cases
        valid_data = {"default_reply": "Стандартный ответ"}
        form = BotDefaultReplyForm(data=valid_data)
        self.assertTrue(form.is_valid())

        # Invalid cases
        invalid_data = [{"default_reply": ""}, {"default_reply": "x" * 3001}]

        for data in invalid_data:
            with self.subTest(data=data):
                form = BotDefaultReplyForm(data=data)
                self.assertFalse(form.is_valid())


class BotMainMenuFormTest(TestCase):
    def test_form_fields(self):
        form = BotMainMenuForm()
        self.assertIn("welcome_message", form.fields)
        self.assertIsInstance(form.fields["welcome_message"], forms.CharField)

    def test_field_attributes(self):
        field = BotMainMenuForm().fields["welcome_message"]
        self.assertEqual(field.label, "Приветственное сообщение:")
        self.assertEqual(field.max_length, 3000)
        self.assertEqual(
            field.widget.attrs["class"], "form-control form-control-user"
        )

    def test_validation(self):
        # Valid cases
        valid_data = {"welcome_message": "Добро пожаловать!"}
        form = BotMainMenuForm(data=valid_data)
        self.assertTrue(form.is_valid())

        # Invalid cases
        invalid_data = [
            {"welcome_message": ""},
            {"welcome_message": "x" * 3001},
        ]

        for data in invalid_data:
            with self.subTest(data=data):
                form = BotMainMenuForm(data=data)
                self.assertFalse(form.is_valid())


class BotMainMenuButtonFormTest(TestCase):
    def test_form_fields(self):
        form = BotMainMenuButtonForm()
        fields = form.fields
        self.assertCountEqual(
            fields.keys(), ["button_text", "reply_text", "chain_id"]
        )
        self.assertIsInstance(fields["button_text"], forms.CharField)
        self.assertIsInstance(fields["reply_text"], forms.CharField)
        self.assertIsInstance(fields["chain_id"], forms.IntegerField)

    def test_field_attributes(self):
        form = BotMainMenuButtonForm()

        # Button text
        btn_field = form.fields["button_text"]
        self.assertEqual(btn_field.label, "Текст кнопки:")
        self.assertEqual(btn_field.max_length, 64)
        self.assertEqual(
            btn_field.widget.attrs["class"], "form-control form-control-user"
        )

        # Reply text
        reply_field = form.fields["reply_text"]
        self.assertEqual(reply_field.label, "Текст ответного сообщения:")
        self.assertEqual(reply_field.max_length, 3000)
        self.assertEqual(
            reply_field.widget.attrs["class"], "form-control form-control-user"
        )

        # Chain ID (should have no widget attrs)
        chain_field = form.fields["chain_id"]
        self.assertEqual(chain_field.widget.attrs, {})

    def test_validation(self):
        # Valid case
        valid_data = {
            "button_text": "Кнопка",
            "reply_text": "Ответ",
            "chain_id": 1,
        }
        form = BotMainMenuButtonForm(data=valid_data)
        self.assertTrue(form.is_valid())

        # Invalid cases
        invalid_cases = [
            {"button_text": "", "reply_text": "Ответ", "chain_id": 1},
            {"button_text": "Кнопка", "reply_text": "", "chain_id": 1},
            {"button_text": "Кнопка", "reply_text": "Ответ", "chain_id": ""},
            {"button_text": "x" * 65, "reply_text": "Ответ", "chain_id": 1},
            {"button_text": "Кнопка", "reply_text": "x" * 3001, "chain_id": 1},
        ]

        for data in invalid_cases:
            with self.subTest(data=data):
                form = BotMainMenuButtonForm(data=data)
                self.assertFalse(form.is_valid())
