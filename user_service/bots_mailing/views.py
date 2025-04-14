import logging

from bots.models import Bot
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import (
    Http404,
    HttpResponse,
    HttpResponseRedirect,
)
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from requests import RequestException

from .utils import (
    send_mail_to_bot_users,
)


logger = logging.getLogger("bots")


class MailingView(LoginRequiredMixin, View):
    """View for managing message broadcasts to bot users"""

    template_name = "bots_mailing/mailing.html"

    def get(self, request, bot_id: int) -> HttpResponse:
        """
        Display mailing form for the bot

        Args:
            request: HttpRequest object
            bot_id: ID of the bot to send messages from

        Returns:
            Rendered template with mailing form

        Raises:
            Http404: If bot doesn't exist or user doesn't have permission
        """
        # Verify bot exists and user has permission
        bot = get_object_or_404(Bot, id=bot_id)
        if bot.user != request.user:
            raise Http404("Permission denied")

        return render(request, self.template_name, {"bot": bot})

    def post(self, request, bot_id: int) -> HttpResponseRedirect:
        """
        Handle mailing form submission

        Args:
            request: HttpRequest with message data
            bot_id: ID of the bot to send messages from

        Returns:
            Redirect to mailing page with status message

        Raises:
            Http404: If bot doesn't exist or user doesn't have permission
        """
        # Verify bot exists and user has permission
        bot = get_object_or_404(Bot, id=bot_id)
        if bot.user != request.user:
            raise Http404("Permission denied")

        message_text = request.POST.get("message_text", "").strip()

        if not message_text:
            messages.error(request, "Текст сообщения не может быть пустым")
            return redirect("mailing", bot_id=bot_id)

        try:
            send_mail_to_bot_users(bot.bot_id, message_text)
            messages.success(request, "Рассылка запущена.")
        except RequestException as e:
            logger.error(
                f"Failed to send mailing for bot {bot_id}. Error: {str(e)}",
                exc_info=True,
            )
            messages.error(
                request,
                "Ошибка при запуске рассылки. Пожалуйста, попробуйте позже",
            )
        except Exception as e:
            logger.critical(
                f"Unexpected error in mailing for bot {bot_id}: {str(e)}",
                exc_info=True,
            )
            messages.error(request, "Произошла непредвиденная ошибка")

        return redirect("mailing", bot_id=bot_id)
