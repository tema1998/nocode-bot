import requests
from bot_management.settings import BOT_SERVICE_API_URL
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.edit import FormView

from .forms import BotForm
from .models import Bot


FASTAPI_URL = "http://127.0.0.1:8080/api/v1/bots"


class CreateBotView(LoginRequiredMixin, FormView):
    template_name = "bots/create_bot.html"  # Шаблон для отображения формы
    form_class = BotForm  # Форма, которую будем использовать
    success_url = reverse_lazy(
        "index"
    )  # URL для перенаправления после успешного создания

    def form_valid(self, form):
        # Получаем данные из формы
        token = form.cleaned_data["token"]

        # Отправляем запрос к FastAPI
        try:
            response = requests.post(
                BOT_SERVICE_API_URL + "bots",
                json={"token": token},
            )
            response.raise_for_status()  # Проверяем на ошибки
        except requests.exceptions.RequestException as e:
            # Если произошла ошибка, возвращаем форму с ошибкой
            return self.form_invalid(form, error=str(e))

        bot_data = response.json()
        bot_id = bot_data["id"]
        bot_username = bot_data["name"]

        # Сохраняем бота в Django
        Bot.objects.create(
            user=self.request.user, bot_id=bot_id, bot_username=bot_username
        )

        # Перенаправляем на страницу успеха
        return super().form_valid(form)

    def form_invalid(self, form, error=None):
        # Добавляем ошибку в контекст, если она есть
        context = self.get_context_data(form=form)
        if error:
            context["error"] = error
        return self.render_to_response(context)
