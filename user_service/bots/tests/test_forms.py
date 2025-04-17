from bots.forms import BotDefaultReplyForm, BotForm
from django import forms
from django.test import TestCase


class BotFormTest(TestCase):
    def test_form_fields(self):
        """Проверка полей формы BotForm"""
        form = BotForm()
        self.assertIn("token", form.fields)
        self.assertIsInstance(form.fields["token"], forms.CharField)

    def test_token_field_attributes(self):
        """Проверка атрибутов поля token"""
        form = BotForm()
        field = form.fields["token"]
        self.assertEqual(field.label, "Token телеграм бота")
        self.assertEqual(field.max_length, 255)
        self.assertEqual(
            field.widget.attrs["class"], "form-control form-control-user"
        )
        self.assertIn("placeholder", field.widget.attrs)

    def test_token_validation(self):
        """Тестирование валидации токена"""
        # Правильные форматы токенов
        valid_tokens = [
            "123456789:ABCdefGHIJKlmNoPQRstuVWXyz",
            "987654321:asdfghjklqwertyuiopzxcvbnm",
            "111111111:AAAAAAAAAAAAAAAAAAAAAAAAAA",
            "123:abc",
        ]

        # Неправильные форматы токенов
        invalid_tokens = [
            "123456789",  # нет двоеточия
            ":ABCdefGHIJKlmNoPQRstuVWXyz",  # нет цифр
            "abc:123",  # цифры после двоеточия
            "123456789:ABC def",  # содержит пробел
            "123456789:ABC!def",  # содержит спецсимвол
        ]

        # Проверка валидных токенов
        for token in valid_tokens:
            with self.subTest(token=token):
                form = BotForm(data={"token": token})
                self.assertTrue(form.is_valid())
                self.assertEqual(form.cleaned_data["token"], token)

        # Проверка невалидных токенов
        for token in invalid_tokens:
            with self.subTest(token=token):
                form = BotForm(data={"token": token})
                self.assertFalse(form.is_valid())
                self.assertIn("token", form.errors)
                self.assertEqual(
                    form.errors["token"][0],
                    "Invalid Telegram token format. Expected format: '123456789:ABCdefGHIJKlmNoPQRstuVWXyz'.",
                )


class BotDefaultReplyFormTest(TestCase):
    def test_form_fields(self):
        """Проверка полей формы BotDefaultReplyForm"""
        form = BotDefaultReplyForm()
        self.assertIn("default_reply", form.fields)
        self.assertIsInstance(form.fields["default_reply"], forms.CharField)

    def test_default_reply_field_attributes(self):
        """Проверка атрибутов поля default_reply"""
        form = BotDefaultReplyForm()
        field = form.fields["default_reply"]
        self.assertEqual(
            field.label, "Ответ бота на неизвестную команду/сообщение:"
        )
        self.assertEqual(field.max_length, 3000)
        self.assertEqual(
            field.widget.attrs["class"], "form-control form-control-user"
        )

    def test_default_reply_validation(self):
        """Тестирование валидации ответа"""
        # Проверка валидных данных
        valid_data = {"default_reply": "Стандартный ответ бота"}
        form = BotDefaultReplyForm(data=valid_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.cleaned_data["default_reply"], valid_data["default_reply"]
        )

        # Проверка пустого значения
        empty_data = {"default_reply": ""}
        form = BotDefaultReplyForm(data=empty_data)
        self.assertFalse(form.is_valid())
        self.assertIn("default_reply", form.errors)

        # Проверка слишком длинного значения
        long_data = {"default_reply": "x" * 3001}
        form = BotDefaultReplyForm(data=long_data)
        self.assertFalse(form.is_valid())
        self.assertIn("default_reply", form.errors)
