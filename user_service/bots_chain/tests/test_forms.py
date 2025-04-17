from bots_chain.forms import BotChainForm  # Импортируем вашу форму
from django import forms
from django.test import TestCase


class BotChainFormTest(TestCase):
    def test_form_has_correct_fields(self):
        """Проверяем, что форма содержит правильные поля"""
        form = BotChainForm()
        self.assertIn("name", form.fields)
        self.assertIsInstance(form.fields["name"], forms.CharField)

    def test_form_field_labels(self):
        """Проверяем правильность лейблов"""
        form = BotChainForm()
        self.assertEqual(form.fields["name"].label, "Название цепочки:")

    def test_form_field_max_length(self):
        """Проверяем максимальную длину поля"""
        form = BotChainForm()
        self.assertEqual(form.fields["name"].max_length, 64)

    def test_form_widget_attrs(self):
        """Проверяем атрибуты виджета"""
        form = BotChainForm()
        widget = form.fields["name"].widget
        self.assertEqual(
            widget.attrs["class"], "form-control form-control-user"
        )

    def test_form_validation(self):
        """Тестируем валидацию формы"""
        # Тест с корректными данными
        valid_data = {"name": "Тестовая цепочка"}
        form = BotChainForm(data=valid_data)
        self.assertTrue(form.is_valid())

        # Тест с пустым значением
        invalid_data = {"name": ""}
        form = BotChainForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)

        # Тест со слишком длинным значением
        long_name = "x" * 65  # Превышаем max_length
        invalid_data = {"name": long_name}
        form = BotChainForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)
