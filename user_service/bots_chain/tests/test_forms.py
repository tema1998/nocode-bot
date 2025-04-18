from bots_chain.forms import (  # Importing the BotChainForm to be tested
    BotChainForm,
)
from django import forms
from django.test import TestCase


class BotChainFormTest(TestCase):
    def test_form_has_correct_fields(self):
        """Verify that the form includes the expected fields."""
        form = BotChainForm()
        self.assertIn("name", form.fields)  # Check if 'name' field exists
        self.assertIsInstance(
            form.fields["name"], forms.CharField
        )  # Ensure 'name' is a CharField

    def test_form_field_labels(self):
        """Ensure that the labels for form fields are correctly defined."""
        form = BotChainForm()
        self.assertEqual(
            form.fields["name"].label, "Название цепочки:"
        )  # Verify the label for 'name' field

    def test_form_field_max_length(self):
        """Validate that the maximum length constraint for the 'name' field is set correctly."""
        form = BotChainForm()
        self.assertEqual(
            form.fields["name"].max_length, 64
        )  # Check if max length is 64 characters

    def test_form_widget_attrs(self):
        """Check that the widget attributes for the 'name' field are correctly configured."""
        form = BotChainForm()
        widget = form.fields["name"].widget
        self.assertEqual(
            widget.attrs["class"],
            "form-control form-control-user",  # Ensure the correct CSS classes are applied
        )

    def test_form_validation(self):
        """Test the validation logic of the form with various input scenarios."""
        # Test case with valid data
        valid_data = {"name": "Test Chain"}
        form = BotChainForm(data=valid_data)
        self.assertTrue(
            form.is_valid()
        )  # The form should be valid with correct data

        # Test case with an empty 'name' field
        invalid_data = {"name": ""}
        form = BotChainForm(data=invalid_data)
        self.assertFalse(form.is_valid())  # The form should be invalid
        self.assertIn("name", form.errors)  # Ensure 'name' field has errors

        # Test case with a 'name' field value that exceeds the maximum length
        long_name = "x" * 65  # Create a string longer than the max length
        invalid_data = {"name": long_name}
        form = BotChainForm(data=invalid_data)
        self.assertFalse(
            form.is_valid()
        )  # The form should be invalid due to length
        self.assertIn(
            "name", form.errors
        )  # Check that 'name' field has a relevant error
