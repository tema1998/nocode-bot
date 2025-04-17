import re

from django import forms


class BotForm(forms.Form):
    token = forms.CharField(
        label="Token телеграм бота",
        max_length=255,
        widget=forms.TextInput(
            attrs={
                "class": "form-control form-control-user",
                "placeholder": "1234567890:QWERTYUIOPasdfghjklZXCVBNMqwertyuio",
            }
        ),
    )

    def clean_token(self):
        token = self.cleaned_data["token"]
        # Регулярное выражение для проверки формата Telegram-токена
        if not re.match(r"^\d+:[a-zA-Z0-9_-]+$", token):
            raise forms.ValidationError(
                "Invalid Telegram token format. Expected format: '123456789:ABCdefGHIJKlmNoPQRstuVWXyz'."
            )
        return token


class BotDefaultReplyForm(forms.Form):
    default_reply = forms.CharField(
        label="Ответ бота на неизвестную команду/сообщение:",
        max_length=3000,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control form-control-user",
            }
        ),
    )
