from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                "class": "form-control form-control-user",
                "placeholder": "Ваш Email адрес",
            }
        ),
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["username"].widget.attrs.update(
            {
                "class": "form-control form-control-user",
                "placeholder": "Ваш логин",
            }
        )
        self.fields["password1"].widget.attrs.update(
            {
                "class": "form-control form-control-user",
                "placeholder": "Ваш пароль",
            }
        )
        self.fields["password2"].widget.attrs.update(
            {
                "class": "form-control form-control-user",
                "placeholder": "Повторите ваш пароль",
            }
        )

        for field_name, field in self.fields.items():
            if self.errors.get(field_name):
                field.widget.attrs.update(
                    {
                        "class": field.widget.attrs.get("class", "")
                        + " is-invalid"
                    }
                )


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control form-control-user",
                "placeholder": "Ваш логин",
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control form-control-user",
                "placeholder": "Ваш пароль",
            }
        )
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if self.errors.get(field_name):
                field.widget.attrs.update(
                    {
                        "class": field.widget.attrs.get("class", "")
                        + " is-invalid"
                    }
                )
