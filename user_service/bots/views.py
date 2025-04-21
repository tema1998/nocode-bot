import logging
from typing import Any, Optional

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import EmptyPage, Paginator
from django.http import (
    Http404,
    HttpResponse,
    HttpResponseRedirect,
)
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic.edit import FormView

from .forms import BotDefaultReplyForm, BotForm
from .models import Bot
from .services import BotService, BotUserService


logger = logging.getLogger("bots")


class BaseBotView(LoginRequiredMixin, View):
    """Base view for bot-related views with common functionality."""

    def get_bot_or_404(self, bot_id: int) -> Bot:
        """Retrieve bot or raise 404, checking ownership."""
        bot: Bot = get_object_or_404(Bot, id=bot_id)
        if bot.user != self.request.user:
            raise Http404("Вы не являетесь владельцем данного бота.")
        return bot


class BotsView(LoginRequiredMixin, View):
    """View to display a list of bots associated with the current user."""

    template_name = "bots/bots.html"

    def get(self, request) -> HttpResponse:
        """Handle GET requests to display user's bots."""
        bots = Bot.objects.filter(user=request.user)
        return render(request, self.template_name, {"bots": bots})


class BotDetailView(BaseBotView):
    """View to display and update bot details."""

    template_name = "bots/bot_details.html"

    def get(self, request, bot_id: int) -> HttpResponse:
        """Display bot details."""
        bot = self.get_bot_or_404(bot_id)

        try:
            bot_data = BotService.get_bot_details(bot.bot_id)
        except Exception as e:
            logger.error(
                f"Failed to fetch bot details. Bot ID: {bot.bot_id}. Error: {str(e)}",
                exc_info=True,
            )
            bot_data = {"username": bot.bot_username, "token_error": True}

        return render(
            request, self.template_name, {"bot": bot, "bot_data": bot_data}
        )

    def post(self, request, bot_id: int) -> HttpResponseRedirect:
        """Update bot details."""
        bot = self.get_bot_or_404(bot_id)
        form = BotForm(request.POST)

        if not form.is_valid():
            messages.error(
                request, "Неверный формат токена. Изменения не были сохранены."
            )
            return redirect("bot-detail", bot_id=bot.id)

        try:
            updated_bot = BotService.update_bot(
                bot_id=bot.bot_id,
                token=form.cleaned_data["token"],
                is_active=request.POST.get("is_active") == "on",
            )
            bot.bot_username = updated_bot["username"]
            bot.save()
            messages.success(request, "Данные бота успешно обновлены.")
        except Exception as e:
            logger.error(
                f"Failed to update bot. Bot ID: {bot.bot_id}. Error: {str(e)}",
                exc_info=True,
            )
            messages.error(
                request,
                "Ошибка при обновлении данных. Проверьте токен, возможно он уже используется другим ботом.",
            )

        return redirect("bot-detail", bot_id=bot.id)


class BotDeleteView(BaseBotView):
    """View to delete a bot."""

    def post(self, request, bot_id: int) -> HttpResponseRedirect:
        """Handle bot deletion."""
        bot = self.get_bot_or_404(bot_id)

        try:
            BotService.delete_bot(bot.bot_id)
            bot_username = bot.bot_username
            bot.delete()
            messages.success(request, f"Бот @{bot_username} успешно удален.")
            return redirect("bots")
        except Exception as e:
            logger.error(
                f"Failed to delete bot. Bot ID: {bot.bot_id}. Error: {str(e)}",
                exc_info=True,
            )
            messages.error(request, "Ошибка при удалении бота.")
            return redirect("bot-detail", bot_id=bot.id)


class AddBotView(LoginRequiredMixin, FormView):
    """View to add a new bot."""

    template_name = "bots/add_bot.html"
    form_class = BotForm

    def form_valid(self, form) -> HttpResponse | Any:
        """Handle valid form submission."""
        try:
            bot_data = BotService.create_bot(form.cleaned_data["token"])
            bot = Bot.objects.create(
                user=self.request.user,
                bot_id=bot_data["id"],
                bot_username=bot_data["username"],
            )
            return redirect("bot-detail", bot_id=bot.id)
        except Exception as e:
            logger.error(
                f"Failed to create bot. Error: {str(e)}",
                exc_info=True,
            )
            return self.form_invalid(
                form,
                error="Токен недействителен либо уже используется другим ботом.",
            )

    def form_invalid(self, form, error: Optional[str] = None) -> HttpResponse:
        """Handle invalid form submission."""
        context = self.get_context_data(form=form)
        if error:
            context["error"] = error
        return self.render_to_response(context)


class BotDefaultReplyView(BaseBotView):
    """View to manage bot's default reply message."""

    template_name = "bots/bot_default_reply.html"

    def get(self, request, bot_id: int) -> HttpResponse:
        """Display current default reply."""
        bot = self.get_bot_or_404(bot_id)

        try:
            bot_data = BotService.get_bot_details(bot.bot_id)
        except Exception as e:
            logger.error(
                f"Failed to fetch bot's default reply. Bot ID: {bot.bot_id}. Error: {str(e)}",
                exc_info=True,
            )
            bot_data = {}

        return render(
            request, self.template_name, {"bot": bot, "bot_data": bot_data}
        )

    def post(self, request, bot_id: int) -> HttpResponseRedirect:
        """Update default reply."""
        bot = self.get_bot_or_404(bot_id)
        form = BotDefaultReplyForm(request.POST)

        if not form.is_valid():
            messages.error(
                request,
                "Текст сообщения слишком большой, ограничение 255 символов.",
            )
            return redirect("bot-default-reply", bot_id=bot.id)

        try:
            BotService.update_bot(
                bot_id=bot.bot_id,
                default_reply=form.cleaned_data["default_reply"],
            )
            messages.success(request, "Успешно обновлено.")
        except Exception as e:
            logger.error(
                f"Failed to update bot. Bot ID: {bot.bot_id}. Error: {str(e)}",
                exc_info=True,
            )
            messages.error(
                request,
                "Ошибка при обновлении данных. Повторите обновление позже.",
            )

        return redirect("bot-default-reply", bot_id=bot.id)


class BotUsersView(BaseBotView):
    """View for displaying paginated bot users."""

    template_name = "bots/bot_users.html"
    USERS_PER_PAGE = 10

    def get(self, request, bot_id: int) -> HttpResponse:
        """Display paginated list of bot users."""
        bot = self.get_bot_or_404(bot_id)

        try:
            page_number = int(request.GET.get("page", 1))
        except ValueError:
            page_number = 1

        users = BotUserService.get_bot_users(bot.bot_id)
        page_obj = self._paginate_users(users, page_number)

        return render(
            request,
            self.template_name,
            {"bot": bot, "page_obj": page_obj},
        )

    def _paginate_users(self, users: list, page_number: int) -> Optional[Any]:
        """Helper method to paginate users."""
        if not users:
            return None

        paginator = Paginator(users, self.USERS_PER_PAGE)
        try:
            return paginator.page(page_number)
        except EmptyPage:
            return paginator.page(1)
