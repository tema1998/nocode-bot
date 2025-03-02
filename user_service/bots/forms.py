import re

from django import forms


class BotForm(forms.Form):
    token = forms.CharField(
        label="Бот Token",
        max_length=255,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    def clean_token(self):
        token = self.cleaned_data["token"]
        # Регулярное выражение для проверки формата Telegram-токена
        if not re.match(r"^\d+:[a-zA-Z0-9_-]+$", token):
            raise forms.ValidationError(
                "Invalid Telegram token format. Expected format: '123456789:ABCdefGHIJKlmNoPQRstuVWXyz'."
            )
        return token
