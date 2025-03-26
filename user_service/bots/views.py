import json
import logging
from typing import Any, Dict

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic.edit import FormView
from requests import RequestException

from .forms import (
    BotChainForm,
    BotDefaultReplyForm,
    BotForm,
    BotMainMenuButtonForm,
    BotMainMenuForm,
)
from .models import Bot
from .utils import (
    create_bot,
    create_chain,
    create_chain_step,
    create_main_menu_button,
    delete_bot,
    delete_bot_main_menu_button,
    delete_chain,
    delete_chain_step,
    get_bot_chain,
    get_bot_chains,
    get_bot_details,
    get_bot_main_menu,
    get_bot_main_menu_button,
    get_chain_step,
    update_bot,
    update_chain,
    update_chain_step,
    update_main_menu,
    update_main_menu_button,
)


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
        """
        # Retrieve the bot from the database
        bot = get_object_or_404(Bot, id=bot_id)

        # Check if the user is the owner of the bot
        if bot.user != request.user:
            raise Http404("Вы не являетесь владельцем данного бота.")

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

        return render(
            request, self.template_name, {"bot": bot, "bot_data": bot_data}
        )

    def post(self, request, bot_id):
        """
        Handles POST requests to update bot details.
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


class BotDeleteView(LoginRequiredMixin, View):

    def post(self, request, bot_id):
        """
        Handles DELETE requests to delete a bot.
        """
        # Retrieve the bot object or return a 404 error if the bot is not found
        bot = get_object_or_404(Bot, id=bot_id)

        # Check if the user is the owner of the bot
        if bot.user != request.user:
            raise Http404("Вы не являетесь владельцем данного бота.")

        try:
            # Delete the bot from the Bot-Service service
            delete_bot(bot.bot_id)  # pass ID of the bot from Bot-service
        except Exception as e:
            # Log the error
            logger.error(
                f"Failed to delete bot. Bot ID: {bot.bot_id}. Error: {str(e)}",
                exc_info=True,
            )
            # If an error occurs during the API request, show an error message and redirect
            messages.error(request, "Ошибка при удалении бота.")
            return redirect("bot-details", bot_id=bot.id)

        bot_username = bot.bot_username

        # Delete the bot from the local database
        bot.delete()

        # Show a success message and redirect to the bot list page
        messages.success(request, f"Бот @{bot_username} успешно удален.")
        return redirect("bots")  # Redirect to the bot list page


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
            raise Http404("Вы не являетесь владельцем данного бота.")

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

        return render(
            request, self.template_name, {"bot": bot, "bot_data": bot_data}
        )

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


class BotMainMenuView(LoginRequiredMixin, View):
    """
    A view for displaying and updating the main menu of a bot.

    This view requires the user to be logged in. It handles both GET and POST requests:
    - GET: Displays the bot's main menu.
    - POST: Updates the bot's welcome message in the main menu.
    """

    template_name = "bots/main_menu.html"  # Template for rendering bot details

    def get(self, request, bot_id: int) -> HttpResponse:
        """
        Handle GET requests to display the bot's main menu.

        Args:
            request: The HTTP request object.
            bot_id (int): The ID of the bot.

        Returns:
            HttpResponse: The rendered template with bot and main menu data.

        Raises:
            Http404: If the bot does not exist or the user is not the owner.
        """
        # Retrieve the bot from the database
        bot = get_object_or_404(Bot, id=bot_id)

        # Check if the user is the owner of the bot
        if bot.user != request.user:
            raise Http404("Вы не являетесь владельцем данного бота.")

        try:
            # Fetch the bot's main menu from the Bot-Service API
            main_menu: Dict[str, Any] = get_bot_main_menu(bot.bot_id)
        except Exception as e:
            # Log the error
            logger.error(
                f"Failed to fetch bot's main menu. Bot ID: {bot.bot_id}. Error: {str(e)}",
                exc_info=True,
            )
            # Return an error response if the request fails
            return HttpResponse(f"An error occurred: {str(e)}", status=500)

        # Render the template with bot and main menu data
        return render(
            request,
            self.template_name,
            {"bot": bot, "bot_main_menu": main_menu},
        )

    def post(self, request, bot_id: int) -> HttpResponse:
        """
        Handle POST requests to update the bot's welcome message.

        Args:
            request: The HTTP request object.
            bot_id (int): The ID of the bot.

        Returns:
            HttpResponse: A redirect to the bot's main menu page.

        Raises:
            Http404: If the bot does not exist or the user is not the owner.
        """
        # Retrieve the bot object or return a 404 error if the bot is not found
        bot = get_object_or_404(Bot, id=bot_id)

        # Validate the form data
        form = BotMainMenuForm(request.POST)
        if not form.is_valid():
            # If the form is invalid, show an error message and redirect
            messages.error(request, "Неверный формат сообщения.")
            return redirect("bot-main-menu", bot_id=bot.id)

        # Extract the welcome message from the form
        welcome_message: str = form.cleaned_data["welcome_message"]

        try:
            # Update the bot's welcome message in the Bot-Service API
            update_main_menu(bot.bot_id, welcome_message)
        except Exception as e:
            # Log the error
            logger.error(
                f"Failed to update bot's main menu. Bot ID: {bot.bot_id}. Error: {str(e)}",
                exc_info=True,
            )
            # If an error occurs during the API request, show an error message and redirect
            messages.error(
                request,
                "Ошибка при обновлении данных. Проверьте формат сообщения!",
            )
            return redirect("bot-main-menu", bot_id=bot.id)

        # If everything is successful, show a success message and redirect
        messages.success(request, "Успешно обновлено.")
        return redirect("bot-main-menu", bot_id=bot.id)


class BotMainMenuButtonView(LoginRequiredMixin, View):
    """
    View for handling the main menu button of a bot.

    This view allows users to view and update the main menu button of a bot.
    Users must be logged in and be the owner of the bot to access this view.
    """

    template_name = "bots/main_menu_button.html"  # Template for rendering the bot's main menu button

    def get(self, request, bot_id: int, button_id: int) -> HttpResponse:
        """
        Handle GET requests to retrieve and display the bot's main menu button.

        Args:
            request: The HTTP request object.
            bot_id (int): The ID of the bot.
            button_id (int): The ID of the button to retrieve.

        Returns:
            HttpResponse: A response containing the rendered template with bot and button data.
        """
        # Retrieve the bot from the database, returning 404 if not found
        bot = get_object_or_404(Bot, id=bot_id)

        # Check if the user is the owner of the bot
        if bot.user != request.user:
            raise Http404("Вы не являетесь владельцем данного бота.")

        try:
            # Fetch the bot's main menu button from the Bot-Service API
            button: Dict[str, Any] = get_bot_main_menu_button(button_id)
        except Exception as e:
            # Log the error if the API request fails
            logger.error(
                f"Failed to fetch bot's main menu button. Bot ID: {bot.bot_id}. Error: {str(e)}",
                exc_info=True,
            )
            # Return an error response if the request fails
            return HttpResponse(f"Произошла ошибка: {str(e)}", status=500)

        # Render the template with bot and main menu button data
        return render(
            request,
            self.template_name,
            {"bot": bot, "button": button},
        )


class UpdateBotMainMenuButtonView(LoginRequiredMixin, View):
    """
    View for handling the update of a bot's main menu button.

    This view processes POST requests to modify the attributes of the
    main menu button in a specified bot. Users must be logged in to
    access this view, and they must have permission to edit the specified bot.

    Attributes:
        login_url (str): URL where users are redirected for login if they are not authenticated.
        redirect_field_name (str): Name of the URL parameter to redirect to after successful login.
    """

    def post(self, request, bot_id: int, button_id: int) -> HttpResponse:
        """
        Handle POST requests to update the bot's main menu button.

        Args:
            request: The HTTP request object.
            bot_id (int): The ID of the bot.
            button_id (int): The ID of the button to update.

        Returns:
            HttpResponse: A redirect response based on the result of the update operation.
        """
        # Retrieve the bot object or return a 404 error if the bot is not found
        bot = get_object_or_404(Bot, id=bot_id)

        # Validate the form data
        form = BotMainMenuButtonForm(request.POST)
        if not form.is_valid():
            # If the form is invalid, show an error message and redirect
            messages.error(request, "Проверьте правильность данных.")
            return redirect(
                "bot-main-menu-button", bot_id=bot.id, button_id=button_id
            )

        # Extract button text and reply text from the form
        button_text: str = form.cleaned_data["button_text"]
        reply_text: str = form.cleaned_data["reply_text"]

        try:
            # Update the bot's main menu button in the Bot-Service API
            update_main_menu_button(button_id, button_text, reply_text)
        except Exception as e:
            # Log the error if the API request fails
            logger.error(
                f"Failed to update bot's main menu button. Button ID: {button_id}. Error: {str(e)}",
                exc_info=True,
            )
            # If an API error occurs, show an error message and redirect
            messages.error(
                request,
                "Ошибка при обновлении данных. Проверьте формат данных!",
            )
            return redirect(
                "bot-main-menu-button", bot_id=bot.id, button_id=button_id
            )

        # If everything is successful, show a success message and redirect
        messages.success(request, "Изменения сохранены.")
        return redirect("bot-main-menu", bot_id=bot.id)


class CreateBotMainMenuButtonView(LoginRequiredMixin, View):
    """
    A view for creating a main menu button for a bot.

    This view handles both GET and POST requests:
    - GET: Renders the form for creating a new button.
    - POST: Processes the form data and creates the button via the Bot-Service API.
    """

    template_name = (
        "bots/create_main_menu_button.html"  # Template for rendering the form
    )

    def get(self, request, bot_id: int) -> HttpResponse:
        """
        Handles GET requests to display the form for creating a new button.

        Args:
            request (HttpRequest): The incoming HTTP request.
            bot_id (int): The ID of the bot for which the button is being created.

        Returns:
            HttpResponse: The rendered template with the bot context.

        Raises:
            Http404: If the bot does not exist or the user is not the owner.
        """
        # Retrieve the bot from the database, returning 404 if not found
        bot = get_object_or_404(Bot, id=bot_id)

        # Check if the user is the owner of the bot
        if bot.user != request.user:
            raise Http404("Вы не являетесь владельцем данного бота.")

        # Render the template with the bot context
        return render(
            request,
            self.template_name,
            {"bot": bot},
        )

    def post(self, request, bot_id: int) -> HttpResponse:
        """
        Handles POST requests to create a new button.

        Args:
            request (HttpRequest): The incoming HTTP request.
            bot_id (int): The ID of the bot for which the button is being created.

        Returns:
            HttpResponse: Redirects to the bot's main menu or the form with error messages.

        Raises:
            Http404: If the bot does not exist or the user is not the owner.
        """
        # Retrieve the bot object or return a 404 error if the bot is not found
        bot = get_object_or_404(Bot, id=bot_id)

        # Validate the form data
        form = BotMainMenuButtonForm(request.POST)
        if not form.is_valid():
            # If the form is invalid, show an error message and redirect
            messages.error(request, "Проверьте правильность данных.")
            return redirect("create-bot-main-menu-button", bot_id=bot.id)

        # Extract button text and reply text from the form
        button_text: str = form.cleaned_data["button_text"]
        reply_text: str = form.cleaned_data["reply_text"]

        try:
            # Create the bot's main menu button via the Bot-Service API
            create_main_menu_button(bot.bot_id, button_text, reply_text)
        except Exception as e:
            # Log the error if the API request fails
            logger.error(
                f"Failed to create bot's main menu button. Bot ID: {bot_id}. Error: {str(e)}",
                exc_info=True,
            )
            # If an API error occurs, show an error message and redirect
            messages.error(
                request,
                "Ошибка при создании кнопки. Проверьте имя цепочка.",
            )
            return redirect("create-bot-main-menu", bot_id=bot.id)

        # If everything is successful, show a success message and redirect
        messages.success(request, "Кнопка успешно создана.")
        return redirect("bot-main-menu", bot_id=bot.id)


class DeleteBotMainMenuButtonView(LoginRequiredMixin, View):
    """
    A view for deleting a main menu button for a bot.

    This view handles POST requests to delete a button via the Bot-Service API.
    """

    def post(self, request, bot_id, button_id):
        """
        Handles POST requests to delete a bot's main menu button.

        Args:
            request (HttpRequest): The incoming HTTP request.
            bot_id (int): The ID of the bot associated with the button.
            button_id (int): The ID of the button to be deleted.

        Returns:
            HttpResponse: Redirects to the bot's main menu with a success or error message.

        Raises:
            Http404: If the bot does not exist or the user is not the owner.
        """
        # Retrieve the bot object or return a 404 error if the bot is not found
        bot = get_object_or_404(Bot, id=bot_id)

        # Check if the user is the owner of the bot
        if bot.user != request.user:
            raise Http404("Вы не являетесь владельцем данного бота.")

        try:
            # Delete the button via the Bot-Service API
            delete_bot_main_menu_button(button_id)
        except Exception as e:
            # Log the error if the API request fails
            logger.error(
                f"Failed to delete button. Button ID: {button_id}. Error: {str(e)}",
                exc_info=True,
            )
            # If an error occurs, show an error message and redirect
            messages.error(
                request, "Ошибка при удалении кнопки. Попробуйте позже."
            )
            return redirect("bot-main-menu", bot_id=bot_id)

        # If successful, show a success message and redirect
        messages.success(request, "Кнопка успешно удалена.")
        return redirect("bot-main-menu", bot_id=bot_id)


class BotChainDetailView(LoginRequiredMixin, View):
    """
    A view to display the details of a bot's chain.

    This view requires the user to be logged in and checks if the user
    is the owner of the bot before fetching its details from an external API.
    """

    template_name = "bots/chain_details.html"

    def get(self, request, bot_id: int, chain_id: int) -> HttpResponse:
        """
        Handle GET requests to retrieve and display the bot's chain details.

        :param request: The HTTP request object.
        :param bot_id: The identifier of the bot.
        :param chain_id: The identifier of the chain to fetch.
        :return: An HttpResponse rendering the bot's chain details.
        :raises Http404: If the bot is not found or the user is not the owner.
        """

        # Retrieve the bot from the database, returning a 404 if not found
        bot = get_object_or_404(Bot, id=bot_id)

        # Check if the user is the owner of the bot
        if bot.user != request.user:
            raise Http404("You are not the owner of this bot.")

        try:
            # Fetch the bot's main menu button from the Bot-Service API
            chain: Dict[str, Any] = get_bot_chain(chain_id)
        except Exception as e:
            # Log the error if the API request fails
            logger.error(
                f"Failed to fetch bot's main menu button. Bot ID: {bot.bot_id}. Error: {str(e)}",
                exc_info=True,
            )
            # Return an error response if the request fails
            return HttpResponse(f"An error occurred: {str(e)}", status=500)

        # Convert the chain data to JSON format for rendering
        chain_json = json.dumps(chain, default=str)

        # Render the template with bot and main menu button data
        return render(
            request,
            self.template_name,
            {"bot": bot, "chain": chain, "chain_json": chain_json},
        )


class BotChainView(LoginRequiredMixin, View):
    """
    View to display bot details by making a GET request to the Bot-Service endpoint.
    """

    template_name = "bots/chains.html"  # Template for rendering bot details

    def get(self, request, bot_id):

        # Retrieve the bot from the database
        bot = get_object_or_404(Bot, id=bot_id)

        # Check if the user is the owner of the bot
        if bot.user != request.user:
            raise Http404("Вы не являетесь владельцем данного бота.")

        try:
            # Fetch bot details from the Bot-Service service
            chains = get_bot_chains(bot.bot_id)
        except Exception as e:
            # Log the error
            logger.error(
                f"Failed to fetch bot details. Bot ID: {bot.bot_id}. Error: {str(e)}",
                exc_info=True,
            )
            # Return an error response if the request fails
            return HttpResponse(f"An error occurred: {str(e)}", status=500)

        return render(
            request,
            self.template_name,
            {"bot": bot, "chains": chains["chains"]},
        )


class CreateChainView(LoginRequiredMixin, View):
    """
    View for creating new chains for a specific bot.

    Attributes:
        template_name (str): Path to the template used for rendering the form.

    Methods:
        get: Handles GET requests - displays the chain creation form.
        post: Handles POST requests - processes the form submission and creates a new chain.
    """

    template_name = "bots/create_chain.html"

    def get(self, request, bot_id: int) -> HttpResponse:
        """
        Handle GET request to display the chain creation form.

        Args:
            request: HttpRequest object
            bot_id: ID of the bot for which the chain is being created

        Returns:
            HttpResponse: Rendered template with bot context

        Raises:
            Http404: If bot doesn't exist or user doesn't own the bot
        """
        bot = get_object_or_404(Bot, id=bot_id)

        if bot.user != request.user:
            logger.warning(
                f"Unauthorized chain creation attempt. User: {request.user.id}, Bot: {bot_id}"
            )
            raise Http404("You are not the owner of this bot.")

        return render(
            request,
            self.template_name,
            {"bot": bot},
        )

    def post(self, request, bot_id: int) -> HttpResponse:
        """
        Handle POST request to create a new chain.

        Args:
            request: HttpRequest object with form data
            bot_id: ID of the bot for which the chain is being created

        Returns:
            HttpResponseRedirect: Redirects to appropriate page with status message

        Raises:
            Http404: If bot doesn't exist
        """
        bot = get_object_or_404(Bot, id=bot_id)
        form = BotChainForm(request.POST)

        if not form.is_valid():
            messages.error(
                request,
                "Проверьте название цепочки, возможно цепочка с таким названием уже существует.",
            )
            return redirect("create-chain", bot_id=bot.id)

        name: str = form.cleaned_data["name"]

        try:
            # Attempt to create chain via API
            create_chain(bot.bot_id, name)
            logger.info(
                f"Chain created successfully. Bot ID: {bot_id}, Chain Name: {name}"
            )
            messages.success(request, "Цепочка успешно создана.")
            return redirect("bot-chains", bot_id=bot.id)

        except Exception as e:
            logger.error(
                f"Failed to create chain. Bot ID: {bot_id}, Error: {str(e)}",
                exc_info=True,
            )
            messages.error(
                request,
                "Проверьте название цепочки, возможно цепочка с таким названием уже существует.",
            )
            return redirect("bot-chains", bot_id=bot.id)


class UpdateChainView(LoginRequiredMixin, View):
    """
    View for updating an existing chain's name for a specific bot.

    This view handles POST requests to update the name of a chain via the Bot-Service API.
    It requires authentication and performs several validations before processing the update.

    Attributes:
        None (inherits from LoginRequiredMixin and View)

    Methods:
        post: Handles the POST request for updating chain information
    """

    def post(self, request, bot_id: int, chain_id: int) -> HttpResponse:
        """
        Handle POST request to update a chain's name.

        Args:
            request: HttpRequest object containing form data
            bot_id: ID of the bot that owns the chain
            chain_id: ID of the chain to be updated

        Returns:
            HttpResponseRedirect: Redirects to appropriate page with status message

        Raises:
            Http404: If the bot doesn't exist or user doesn't own it
        """

        # Retrieve the bot object or return 404
        bot = get_object_or_404(Bot, id=bot_id)

        # Verify user owns the bot
        if bot.user != request.user:
            logger.warning(
                f"Unauthorized chain update attempt. User: {request.user.id}, Bot: {bot_id}"
            )
            raise Http404("You don't have permission to update this chain.")

        # Validate form data
        form = BotChainForm(request.POST)
        if not form.is_valid():
            messages.error(request, "Проверьте правильность введенных данных.")
            return redirect("update-chain", bot_id=bot.id, chain_id=chain_id)

        new_name: str = form.cleaned_data["name"]

        try:
            # Attempt to update chain via API
            update_chain(chain_id, new_name)
            logger.info(
                f"Chain updated successfully. Bot ID: {bot_id}, Chain ID: {chain_id}, New Name: '{new_name}'"
            )
            messages.success(request, "Цепочка успешно обновлена.")
            return redirect("bot-chain", bot_id=bot.id, chain_id=chain_id)

        except RequestException as e:
            # Handle API request errors
            logger.error(
                f"API request failed during chain update. Bot ID: {bot_id}, Chain ID: {chain_id}, Error: {str(e)}",
                exc_info=True,
            )
            messages.error(
                request,
                "Ошибка при обновлении цепочки. Пожалуйста, попробуйте позже.",
            )
            return redirect("update-chain", bot_id=bot.id, chain_id=chain_id)

        except Exception as e:
            # Handle unexpected errors
            logger.critical(
                f"Unexpected error during chain update. Bot ID: {bot_id}, Chain ID: {chain_id}, Error: {str(e)}",
                exc_info=True,
            )
            messages.error(
                request,
                "Произошла непредвиденная ошибка. Пожалуйста, свяжитесь с поддержкой.",
            )
            return redirect("update-chain", bot_id=bot.id, chain_id=chain_id)


class DeleteChainView(LoginRequiredMixin, View):
    """
    View for deleting a chain via the Bot-Service API.

    Handles POST requests to delete a chain after verifying ownership and API communication.

    Attributes:
        None (inherits from LoginRequiredMixin and View)

    Methods:
        post: Handles the chain deletion request
    """

    def post(
        self, request, bot_id: int, chain_id: int
    ) -> HttpResponseRedirect:
        """
        Handle chain deletion request.

        Args:
            request: HttpRequest object
            bot_id: ID of the bot owning the chain
            chain_id: ID of the chain to delete

        Returns:
            HttpResponseRedirect: Redirects to chains list with status message

        Raises:
            Http404: If bot doesn't exist or user doesn't own it
        """
        # Validate and get bot object
        bot = get_object_or_404(Bot, id=bot_id)

        # Verify ownership
        if bot.user != request.user:
            logger.warning(
                f"Unauthorized chain deletion attempt. User: {request.user.id}, Bot: {bot_id}"
            )
            raise Http404("Вы не являетесь владельцем данного бота.")

        try:
            # Log deletion attempt
            logger.info(
                f"Attempting to delete chain. Bot ID: {bot_id}, Chain ID: {chain_id}"
            )

            # Call API to delete chain
            delete_chain(chain_id)

            # Log success
            logger.info(
                f"Successfully deleted chain. Bot ID: {bot_id}, Chain ID: {chain_id}"
            )

            messages.success(request, "Цепочка успешно удалена.")
            return redirect("bot-chains", bot_id=bot_id)

        except RequestException as e:
            # Handle API communication errors
            logger.error(
                f"API error deleting chain. Bot ID: {bot_id}, Chain ID: {chain_id}, Error: {str(e)}",
                exc_info=True,
                extra={
                    "bot_id": bot_id,
                    "chain_id": chain_id,
                    "user_id": request.user.id,
                },
            )
            messages.error(
                request,
                "Ошибка при удалении цепочки. Пожалуйста, попробуйте позже.",
            )
            return redirect("bot-chains", bot_id=bot_id)

        except Exception as e:
            # Handle unexpected errors
            logger.critical(
                f"Unexpected error deleting chain. Bot ID: {bot_id}, Chain ID: {chain_id}, Error: {str(e)}",
                exc_info=True,
                extra={
                    "bot_id": bot_id,
                    "chain_id": chain_id,
                    "user_id": request.user.id,
                },
            )
            messages.error(
                request,
                "Произошла непредвиденная ошибка при удалении. Пожалуйста, свяжитесь с поддержкой.",
            )
            return redirect("bot-chains", bot_id=bot_id)


class CreateChainStepView(LoginRequiredMixin, View):
    """View for creating new chain steps in conversation flows."""

    def post(
        self, request, bot_id: int, chain_id: int
    ) -> HttpResponseRedirect:
        """
        Handle step creation request.

        Args:
            request: HttpRequest object
            bot_id: ID of the bot that owns the chain
            chain_id: ID of the chain to add step to

        Returns:
            Redirect to chain view or error page

        Raises:
            Http404: If user doesn't own the bot or other access violation
        """
        bot = get_object_or_404(Bot, id=bot_id)

        if bot.user != request.user:
            raise Http404("You don't have permission to modify this bot.")

        try:
            create_chain_step(
                chain_id=chain_id,
                name="<Не задано>",
                message="<Не задано>",
                is_first_step_of_chain=request.POST.get(
                    "is_first_step_of_chain"
                )
                == "true",
                set_as_next_step_for_button_id=request.POST.get(
                    "set_as_next_step_for_button_id"
                ),
            )
            messages.success(
                request,
                "Шаг успешно создан. Отредактируйте его содержимое и добавьте к нему кнопки с вариантами ответа для пользователя.",
            )
            return redirect("bot-chain", bot_id=bot_id, chain_id=chain_id)

        except Exception as e:
            logger.error(
                f"Failed to create chain step. Chain ID: {chain_id}. Error: {str(e)}",
                exc_info=True,
            )
            messages.error(request, f"Ошибка при создании шага: {str(e)}")
            return redirect("bot-chain", bot_id=bot_id, chain_id=chain_id)


class UpdateChainStepView(LoginRequiredMixin, View):
    """View for updating existing chain steps in conversation flows."""

    template_name = "bots/update_chain_step.html"

    def get(
        self, request, bot_id: int, chain_id: int, step_id: int
    ) -> HttpResponse:
        """
        Render step editing form.

        Args:
            request: HttpRequest object
            bot_id: ID of the bot that owns the chain
            chain_id: ID of the chain containing the step
            step_id: ID of the step to edit

        Returns:
            Rendered template with step data

        Raises:
            Http404: If user doesn't own the bot or step not found
        """
        bot = get_object_or_404(Bot, id=bot_id)

        if bot.user != request.user:
            raise Http404("You don't have permission to modify this bot.")

        step = get_chain_step(step_id)
        return render(
            request,
            self.template_name,
            {
                "bot": bot,
                "chain_id": chain_id,
                "step": step,
            },
        )

    def post(
        self, request, bot_id: int, chain_id: int, step_id: int
    ) -> HttpResponseRedirect:
        """
        Handle step update request.

        Args:
            request: HttpRequest with updated step data
            bot_id: ID of the bot that owns the chain
            chain_id: ID of the chain containing the step
            step_id: ID of the step to update

        Returns:
            Redirect to chain view or back to edit form on error

        Raises:
            Http404: If user doesn't own the bot
        """
        bot = get_object_or_404(Bot, id=bot_id)

        if bot.user != request.user:
            raise Http404("You don't have permission to modify this bot.")

        try:
            update_chain_step(
                step_id=step_id,
                name=request.POST.get("name"),
                message=request.POST.get("message"),
            )
            messages.success(request, "Шаг успешно обновлен.")
            return redirect("bot-chain", bot_id=bot_id, chain_id=chain_id)

        except Exception as e:
            logger.error(
                f"Failed to update chain step. Step ID: {step_id}. Error: {str(e)}",
                exc_info=True,
            )
            messages.error(request, f"Ошибка при обновлении шага: {str(e)}")
            return redirect(
                "update-chain-step",
                bot_id=bot_id,
                chain_id=chain_id,
                step_id=step_id,
            )


class DeleteChainStepView(LoginRequiredMixin, View):
    """View for deleting chain steps from conversation flows."""

    def post(
        self, request, bot_id: int, chain_id: int, step_id: int
    ) -> HttpResponseRedirect:
        """
        Handle step deletion request.

        Args:
            request: HttpRequest object
            bot_id: ID of the bot that owns the chain
            chain_id: ID of the chain containing the step
            step_id: ID of the step to delete

        Returns:
            Redirect to chain view

        Raises:
            Http404: If user doesn't own the bot
        """
        bot = get_object_or_404(Bot, id=bot_id)

        if bot.user != request.user:
            raise Http404("You don't have permission to modify this bot.")

        try:
            delete_chain_step(step_id)
            messages.success(request, "Шаг успешно удален.")
        except Exception as e:
            logger.error(
                f"Failed to delete chain step. Step ID: {step_id}. Error: {str(e)}",
                exc_info=True,
            )
            messages.error(request, "Ошибка при удалении шага.")

        return redirect("bot-chain", bot_id=bot_id, chain_id=chain_id)
