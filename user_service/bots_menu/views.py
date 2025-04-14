from bots.models import Bot
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from requests import RequestException

from .forms import BotMainMenuButtonForm, BotMainMenuForm
from .services import BotServiceClient


class BaseBotView(LoginRequiredMixin, View):
    """Base view for bot-related operations with common functionality."""

    def validate_bot_ownership(self, request, bot_id: int) -> Bot:
        """Validate that the user owns the bot and return the bot instance."""
        bot = get_object_or_404(Bot, id=bot_id)
        if bot.user != request.user:
            raise Http404("Вы не являетесь владельцем данного бота.")
        return bot


class BotMainMenuView(BaseBotView):
    """View for displaying and updating the main menu of a bot."""

    template_name = "bots_menu/main_menu.html"

    def get(self, request, bot_id: int) -> HttpResponse:
        bot = self.validate_bot_ownership(request, bot_id)

        try:
            main_menu = BotServiceClient.get_main_menu(bot.bot_id)
        except RequestException:
            main_menu = {}

        return render(
            request,
            self.template_name,
            {"bot": bot, "bot_main_menu": main_menu},
        )

    def post(self, request, bot_id: int) -> HttpResponse:
        bot = self.validate_bot_ownership(request, bot_id)
        form = BotMainMenuForm(request.POST)

        if not form.is_valid():
            messages.error(request, "Неверный формат сообщения.")
            return redirect("bot-main-menu", bot_id=bot.id)

        try:
            BotServiceClient.update_main_menu(
                bot.bot_id, form.cleaned_data["welcome_message"]
            )
            messages.success(request, "Успешно обновлено.")
        except RequestException:
            messages.error(
                request,
                "Ошибка при обновлении данных. Проверьте формат сообщения!",
            )

        return redirect("bot-main-menu", bot_id=bot.id)


class BotMainMenuButtonView(BaseBotView):
    """View for handling the main menu button of a bot."""

    template_name = "bots_menu/update_main_menu_button.html"

    def get(self, request, bot_id: int, button_id: int) -> HttpResponse:
        bot = self.validate_bot_ownership(request, bot_id)

        try:
            button = BotServiceClient.get_main_menu_button(button_id)
            chains_response = BotServiceClient.get_bot_chains(bot.bot_id)
        except RequestException:
            chains_response = {"chains": {}}

        return render(
            request,
            self.template_name,
            {
                "bot": bot,
                "button": button,
                "chains": chains_response["chains"],
            },
        )


class UpdateBotMainMenuButtonView(BaseBotView):
    """View for updating a bot's main menu button."""

    def post(self, request, bot_id: int, button_id: int) -> HttpResponse:
        bot = self.validate_bot_ownership(request, bot_id)
        form = BotMainMenuButtonForm(request.POST)

        if not form.is_valid():
            messages.error(request, "Проверьте правильность данных.")
            return redirect(
                "bot-main-menu-button", bot_id=bot.id, button_id=button_id
            )

        try:
            BotServiceClient.update_main_menu_button(
                button_id,
                button_text=form.cleaned_data["button_text"],
                reply_text=form.cleaned_data["reply_text"],
                chain_id=form.cleaned_data["chain_id"] or None,
            )
            messages.success(request, "Изменения сохранены.")
        except RequestException:
            messages.error(
                request,
                "Ошибка при обновлении данных. Проверьте формат данных!",
            )

        return redirect("bot-main-menu", bot_id=bot.id)


class CreateBotMainMenuButtonView(BaseBotView):
    """View for creating a main menu button for a bot."""

    template_name = "bots_menu/create_main_menu_button.html"

    def get(self, request, bot_id: int) -> HttpResponse:
        bot = self.validate_bot_ownership(request, bot_id)

        try:
            chains_response = BotServiceClient.get_bot_chains(bot.bot_id)
        except RequestException:
            chains_response = {"chains": {}}

        return render(
            request,
            self.template_name,
            {"bot": bot, "chains": chains_response["chains"]},
        )

    def post(self, request, bot_id: int) -> HttpResponse:
        bot = self.validate_bot_ownership(request, bot_id)
        form = BotMainMenuButtonForm(request.POST)

        if not form.is_valid():
            messages.error(request, "Проверьте правильность данных.")
            return redirect("create-bot-main-menu-button", bot_id=bot.id)

        try:
            BotServiceClient.create_main_menu_button(
                bot.bot_id,
                button_text=form.cleaned_data["button_text"],
                reply_text=form.cleaned_data["reply_text"],
                chain_id=form.cleaned_data["chain_id"] or None,
            )
            messages.success(request, "Кнопка успешно создана.")
        except RequestException:
            messages.error(
                request,
                "Ошибка при создании кнопки. Возможно такая кнопка уже существует.",
            )

        return redirect("bot-main-menu", bot_id=bot.id)


class DeleteBotMainMenuButtonView(BaseBotView):
    """View for deleting a main menu button for a bot."""

    def post(self, request, bot_id: int, button_id: int) -> HttpResponse:
        self.validate_bot_ownership(request, bot_id)

        try:
            BotServiceClient.delete_main_menu_button(button_id)
            messages.success(request, "Кнопка успешно удалена.")
        except RequestException:
            messages.error(
                request, "Ошибка при удалении кнопки. Попробуйте позже."
            )

        return redirect("bot-main-menu", bot_id=bot_id)
