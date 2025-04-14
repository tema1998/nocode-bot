from django import forms


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
