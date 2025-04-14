import logging
from typing import Any, Dict

from bots.models import Bot
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import (
    Http404,
    HttpResponse,
)
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from .forms import BotMainMenuButtonForm, BotMainMenuForm
from .utils import (
    create_main_menu_button,
    delete_bot_main_menu_button,
    get_bot_chains,
    get_bot_main_menu,
    get_bot_main_menu_button,
    update_main_menu,
    update_main_menu_button,
)


logger = logging.getLogger("bots")


class BotMainMenuView(LoginRequiredMixin, View):
    """
    A view for displaying and updating the main menu of a bot.

    This view requires the user to be logged in. It handles both GET and POST requests:
    - GET: Displays the bot's main menu.
    - POST: Updates the bot's welcome message in the main menu.
    """

    template_name = (
        "bots_menu/main_menu.html"  # Template for rendering bot details
    )

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
            main_menu = {}

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

    template_name = "bots_menu/update_main_menu_button.html"  # Template for rendering the bot's main menu button

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

            chains_response: Dict[str, Any] = get_bot_chains(bot.bot_id)
        except Exception as e:
            # Log the error if the API request fails
            logger.error(
                f"Failed to fetch bot's main menu button. Bot ID: {bot.bot_id}. Error: {str(e)}",
                exc_info=True,
            )
            chains_response = {"chains": {}}

        # Render the template with bot and main menu button data
        return render(
            request,
            self.template_name,
            {
                "bot": bot,
                "button": button,
                "chains": chains_response["chains"],
            },
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

        # Extract button text,reply text and chain_id from the form
        button_text: str = form.cleaned_data["button_text"]
        reply_text: str = form.cleaned_data["reply_text"]
        chain_id = form.cleaned_data["chain_id"]
        chain_id = chain_id if chain_id != 0 else None

        try:
            # Update the bot's main menu button in the Bot-Service API
            update_main_menu_button(
                button_id, button_text, reply_text, chain_id
            )
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

    template_name = "bots_menu/create_main_menu_button.html"  # Template for rendering the form

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
        try:
            chains_response: Dict[str, Any] = get_bot_chains(bot.bot_id)
        except Exception as e:
            logger.error(
                f"Failed to fetch chains of the bot. Bot ID: {bot.bot_id}. Error: {str(e)}",
                exc_info=True,
            )
            chains_response = {"chains": {}}

        # Render the template with the bot context
        return render(
            request,
            self.template_name,
            {"bot": bot, "chains": chains_response["chains"]},
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

        # Extract button text,reply text and chain_id from the form
        button_text: str = form.cleaned_data["button_text"]
        reply_text: str = form.cleaned_data["reply_text"]
        chain_id = form.cleaned_data["chain_id"]
        chain_id = chain_id if chain_id != 0 else None

        try:
            # Create the bot's main menu button via the Bot-Service API
            create_main_menu_button(
                bot.bot_id, button_text, reply_text, chain_id
            )
        except Exception as e:
            # Log the error if the API request fails
            logger.error(
                f"Failed to create bot's main menu button. Bot ID: {bot_id}. Error: {str(e)}",
                exc_info=True,
            )
            # If an API error occurs, show an error message and redirect
            messages.error(
                request,
                "Ошибка при создании кнопки. Возможно такая кнопка уже существует.",
            )
            return redirect("create-bot-main-menu-button", bot_id=bot.id)

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
