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
        widget=forms.TextInput(
            attrs={
                "class": "form-control form-control-user",
            }
        ),
    )


class BotMainMenuForm(forms.Form):
    welcome_message = forms.CharField(
        label="Приветственное сообщение:",
        max_length=3000,
        widget=forms.TextInput(
            attrs={
                "class": "form-control form-control-user",
            }
        ),
    )


class BotMainMenuButtonForm(forms.Form):
    button_text = forms.CharField(
        label="Текст кнопки:",
        max_length=64,
        widget=forms.TextInput(
            attrs={
                "class": "form-control form-control-user",
            }
        ),
    )

    reply_text = forms.CharField(
        label="Текст ответного сообщения:",
        max_length=3000,
        widget=forms.TextInput(
            attrs={
                "class": "form-control form-control-user",
            }
        ),
    )
    chain_id = forms.IntegerField()


class BotChainForm(forms.Form):
    name = forms.CharField(
        label="Название цепочки:",
        max_length=64,
        widget=forms.TextInput(
            attrs={
                "class": "form-control form-control-user",
            }
        ),
    )
