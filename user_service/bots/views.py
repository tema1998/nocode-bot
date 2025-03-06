import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic.edit import FormView

from .forms import BotDefaultReplyForm, BotForm
from .models import Bot
from .utils import create_bot, get_bot_details, update_bot


logger = logging.getLogger("bots")


class BotsView(LoginRequiredMixin, View):
    """
    View to display a list of bots associated with the current user.
    """

    template_name = "bots/bots.html"  # Template for rendering the bot list

    def get(self, request):
        """
        Handles GET requests and returns a list of bots for the current user.

        Args:
            request (HttpRequest): The request object.

        Returns:
            HttpResponse: Rendered template with the list of bots.
        """
        # Retrieve bots associated with the current user
        bots = Bot.objects.filter(user=request.user)

        # Render the template with the bots
        return render(request, self.template_name, {"bots": bots})


class BotDetailView(LoginRequiredMixin, View):
    """
    View to display bot details by making a GET request to the Bot-Service endpoint.
    """

    template_name = (
        "bots/bot_details.html"  # Template for rendering bot details
    )

    def get(self, request, bot_id):
        """
        Handles GET requests to display bot details.

        Args:
            request (HttpRequest): The request object.
            bot_id (int): The ID of the bot to retrieve.

        Returns:
            HttpResponse: Rendered template with bot details.

        Raises:
            Http404: If the bot is not found or the user is not the owner.
        """
        # Retrieve the bot from the database
        bot = get_object_or_404(Bot, id=bot_id)

        # Check if the user is the owner of the bot
        if bot.user != request.user:
            raise Http404("You are not the owner of this bot.")

        try:
            # Fetch bot details from the Bot-Service service
            bot_data = get_bot_details(bot.bot_id)
        except Exception as e:
            # Log the error
            logger.error(
                f"Failed to fetch bot details. Bot ID: {bot.bot_id}. Error: {str(e)}",
                exc_info=True,
            )
            # Return an error response if the request fails
            return HttpResponse(f"An error occurred: {str(e)}", status=500)

        # Add the user_service bot ID to the response data
        bot_data["id"] = bot.id

        return render(request, self.template_name, {"bot": bot_data})

    def post(self, request, bot_id):
        """
        Handles POST requests to update bot details.

        Args:
            request (HttpRequest): The request object.
            bot_id (int): The ID of the bot to update.

        Returns:
            HttpResponseRedirect: Redirects to the bot details page.
        """
        # Retrieve the bot object or return a 404 error if the bot is not found
        bot = get_object_or_404(Bot, id=bot_id)

        # Update the `is_active` and `token` fields
        is_active = (
            request.POST.get("is_active") == "on"
        )  # The toggle returns 'on' or None
        form = BotForm(request.POST)

        # Validate token
        if form.is_valid():
            token = form.cleaned_data["token"]
        else:
            # If the form is invalid, show an error message and redirect
            messages.error(
                request, "Неверный формат токена. Изменения не были сохранены."
            )
            return redirect("bot-details", bot_id=bot.id)

        try:
            # Update bot data in the Bot-Service service
            update_bot(bot.bot_id, token, is_active)
        except Exception as e:
            # Log the error
            logger.error(
                f"Failed to update bot. Bot ID: {bot.bot_id}. Error: {str(e)}",
                exc_info=True,
            )
            # If an error occurs during the API request, show an error message and redirect
            messages.error(
                request,
                "Ошибка при обновлении данных. Проверьте токен!",
            )
            return redirect("bot-details", bot_id=bot.id)

        # If everything is successful, show a success message and redirect
        messages.success(request, "Данные бота успешно обновлены.")
        return redirect("bot-details", bot_id=bot.id)


class AddBotView(LoginRequiredMixin, FormView):
    """
    View to add a new bot by submitting a form.
    """

    template_name = "bots/add_bot.html"  # Template for rendering the form
    form_class = BotForm  # Form class to use for bot creation

    def form_valid(self, form):
        """
        Handles valid form submissions.

        Args:
            form (BotForm): The validated form instance.

        Returns:
            HttpResponseRedirect: Redirects to the success URL.
        """
        # Extract the token from the form
        token = form.cleaned_data["token"]

        try:
            # Create a new bot in the Bot-service service
            bot_data = create_bot(token)
            bot_id = bot_data["id"]  # Bot ID of the Bot-service
            bot_username = bot_data["username"]

            # Save the bot in the Django database
            bot = Bot.objects.create(
                user=self.request.user,
                bot_id=bot_id,
                bot_username=bot_username,
            )
        except Exception as e:
            # Log the error
            logger.error(
                f"Failed to create bot. Token: {token}. Error: {str(e)}",
                exc_info=True,
            )
            # If an error occurs, return the form with an error message
            return self.form_invalid(form, error=str(e))

        # Redirect to the success URL
        return redirect("bot-details", bot_id=bot.id)

    def form_invalid(self, form, error=None):
        """
        Handles invalid form submissions.

        Args:
            form (BotForm): The invalid form instance.
            error (str, optional): An error message to display. Defaults to None.

        Returns:
            HttpResponse: Rendered template with the form and error message.
        """
        # Add the error to the context if provided
        context = self.get_context_data(form=form)
        if error:
            context["error"] = error

        # Render the template with the form and error
        return self.render_to_response(context)


class BotDefaultReplyView(LoginRequiredMixin, View):
    """
    View to display/patch bot default reply by making a GET/PATCH request to the Bot-Service endpoint.
    """

    template_name = (
        "bots/bot_default_reply.html"  # Template for rendering bot details
    )

    def get(self, request, bot_id):
        """
        Handles GET requests to display bot details.

        Args:
            request (HttpRequest): The request object.
            bot_id (int): The ID of the bot to retrieve.

        Returns:
            HttpResponse: Rendered template with bot details.

        Raises:
            Http404: If the bot is not found or the user is not the owner.
        """
        # Retrieve the bot from the database
        bot = get_object_or_404(Bot, id=bot_id)

        # Check if the user is the owner of the bot
        if bot.user != request.user:
            raise Http404("You are not the owner of this bot.")

        try:
            # Fetch bot details from the Bot-Service service
            bot_data = get_bot_details(bot.bot_id)
        except Exception as e:
            # Log the error
            logger.error(
                f"Failed to fetch bot details. Bot ID: {bot.bot_id}. Error: {str(e)}",
                exc_info=True,
            )
            # Return an error response if the request fails
            return HttpResponse(f"An error occurred: {str(e)}", status=500)

        # Add the user_service bot ID to the response data
        bot_data["id"] = bot.id

        return render(request, self.template_name, {"bot": bot_data})

    def post(self, request, bot_id):
        """
        Handles POST requests to update bot's default reply.

        Args:
            request (HttpRequest): The request object.
            bot_id (int): The ID of the bot to update.

        Returns:
            HttpResponseRedirect: Redirects to the bot details page.
        """
        # Retrieve the bot object or return a 404 error if the bot is not found
        bot = get_object_or_404(Bot, id=bot_id)

        form = BotDefaultReplyForm(request.POST)

        # Validate default_reply
        if form.is_valid():
            default_reply = form.cleaned_data["default_reply"]
        else:
            # If the form is invalid, show an error message and redirect
            messages.error(
                request,
                "Текст сообщения слишком большой, ограничение 255 символов.",
            )
            return redirect("bot-default-reply", bot_id=bot.id)

        try:
            # Update bot's default reply in the Bot-Service service
            update_bot(bot_id=bot.bot_id, default_reply=default_reply)
        except Exception as e:
            # Log the error
            logger.error(
                f"Failed to update bot. Bot ID: {bot.bot_id}. Error: {str(e)}",
                exc_info=True,
            )
            # If an error occurs during the API request, show an error message and redirect
            messages.error(
                request,
                "Ошибка при обновлении данных. Повторите обновление позже.",
            )
            return redirect("bot-default-reply", bot_id=bot.id)

        # If everything is successful, show a success message and redirect
        messages.success(request, "Успешно обновлено.")
        return redirect("bot-default-reply", bot_id=bot.id)
