from django.urls import path

from .views import CreateBotView


urlpatterns = [
    path("", CreateBotView.as_view(), name="bot"),
]
