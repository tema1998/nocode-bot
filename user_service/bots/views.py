import requests
from bot_management.settings import BOT_SERVICE_API_URL
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.edit import FormView

from .forms import BotForm
from .models import Bot


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


class AddBotView(LoginRequiredMixin, FormView):
    """
    View to add a new bot by submitting a form.
    """

    template_name = "bots/add_bot.html"  # Template for rendering the form
    form_class = BotForm  # Form class to use for bot creation
    success_url = reverse_lazy(
        "index"
    )  # URL to redirect to after successful bot creation

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
            # Send a POST request to the FastAPI service to create a bot
            response = requests.post(
                BOT_SERVICE_API_URL + "bots",
                json={"token": token},
            )
            response.raise_for_status()  # Raise an exception for HTTP errors
        except requests.exceptions.RequestException as e:
            # If an error occurs, return the form with an error message
            return self.form_invalid(form, error=str(e))

        # Extract bot data from the response
        bot_data = response.json()
        bot_id = bot_data["id"]
        bot_username = bot_data["name"]

        # Save the bot in the Django database
        Bot.objects.create(
            user=self.request.user, bot_id=bot_id, bot_username=bot_username
        )

        # Redirect to the success URL
        return super().form_valid(form)

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
