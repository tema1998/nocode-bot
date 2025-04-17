import logging

from bots.models import Bot
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from requests.exceptions import RequestException

from .services import MailingService


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
        bot = self._get_authorized_bot(bot_id)
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
        bot = self._get_authorized_bot(bot_id)
        message_text = request.POST.get("message_text", "").strip()

        if not message_text:
            messages.error(request, "Текст сообщения не может быть пустым.")
            return redirect("mailing", bot_id=bot_id)

        try:
            MailingService.send_mailing(bot.bot_id, message_text)
            messages.success(request, "Рассылка запущена.")
        except RequestException as e:
            logger.error(
                f"Mailing failed for bot {bot_id}: {str(e)}", exc_info=True
            )
            messages.error(
                request, "Ошибка запуска рассылки. Попробуйте повторить позже."
            )
        except Exception as e:
            logger.critical(
                f"Unexpected error in mailing for bot {bot_id}: {str(e)}",
                exc_info=True,
            )
            messages.error(
                request, "Ошибка запуска рассылки. Попробуйте повторить позже."
            )

        return redirect("mailing", bot_id=bot_id)

    def _get_authorized_bot(self, bot_id: int) -> Bot:
        """Get bot and verify user permission"""
        bot = get_object_or_404(Bot, id=bot_id)
        if bot.user != self.request.user:
            raise Http404("Permission denied")
        return bot
