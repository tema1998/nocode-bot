from django.urls import path

from .views import (
    MailingView,
)


urlpatterns = [
    path("bots/<int:bot_id>/mailing/", MailingView.as_view(), name="mailing")
]
