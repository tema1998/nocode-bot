import json
import logging
from typing import Any, Dict

from bots.models import Bot
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
from requests import RequestException

from .forms import BotChainForm
from .utils import (
    create_chain,
    create_chain_button,
    create_chain_step,
    delete_chain,
    delete_chain_button,
    delete_chain_step,
    get_bot_chain,
    get_bot_chains,
    get_chain_button,
    get_chain_step,
    get_paginated_chain_results,
    update_chain,
    update_chain_button,
    update_chain_step,
)


logger = logging.getLogger("bots")


class BotChainDetailView(LoginRequiredMixin, View):
    """
    A view to display the details of a bot's chain.

    This view requires the user to be logged in and checks if the user
    is the owner of the bot before fetching its details from an external API.
    """

    template_name = "bots_chain/chain_details.html"

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
                f"Failed to fetch chain. Chain ID: {chain_id}. Error: {str(e)}",
                exc_info=True,
            )
            # Return an error response if the request fails
            chain = {}

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

    template_name = (
        "bots_chain/chains.html"  # Template for rendering bot details
    )

    def get(self, request, bot_id):

        # Retrieve the bot from the database
        bot = get_object_or_404(Bot, id=bot_id)

        # Check if the user is the owner of the bot
        if bot.user != request.user:
            raise Http404("Вы не являетесь владельцем данного бота.")

        try:
            # Fetch bot details from the Bot-Service service
            chains_response = get_bot_chains(bot.bot_id)
        except Exception as e:
            # Log the error
            logger.error(
                f"Failed to fetch chains of the bot. Bot ID: {bot.bot_id}. Error: {str(e)}",
                exc_info=True,
            )
            # Return an error response if the request fails
            chains_response = {"chains": {}}

        return render(
            request,
            self.template_name,
            {"bot": bot, "chains": chains_response["chains"]},
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

    template_name = "bots_chain/create_chain.html"

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


class CreateChainStepTextinputView(LoginRequiredMixin, View):
    """View for creating new chain steps after text input."""

    def post(
        self, request, bot_id: int, chain_id: int
    ) -> HttpResponseRedirect:
        """
        Handle step creation request for textinput field.

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

            response = create_chain_step(
                chain_id=chain_id, name="<Не задано>", message="<Не задано>"
            )

            update_chain_step(
                step_id=int(request.POST.get("set_as_next_step_for_step_id")),
                next_step_id=int(response["id"]),
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


class EditTextinputView(LoginRequiredMixin, View):
    """View for turn off/on text input of the step."""

    def post(
        self, request, bot_id: int, chain_id: int, step_id: int
    ) -> HttpResponseRedirect:
        """
        Turn off/on text input of the step.

        Args:
            request: HttpRequest object
            bot_id: ID of the bot that owns the chain
            chain_id: ID of the chain
            step_id: ID of the step

        Returns:
            Redirect to chain view or error page

        Raises:
            Http404: If user doesn't own the bot or other access violation
        """
        bot = get_object_or_404(Bot, id=bot_id)

        if bot.user != request.user:
            raise Http404("You don't have permission to modify this bot.")

        try:
            text_input = request.POST.get("text_input") == "on"
            update_chain_step(
                step_id=int(step_id),
                text_input=text_input,
            )

            if text_input:
                messages.success(
                    request,
                    "Текстовый ввод успешно создан. Для продолжения его цепочки - добавить к нему следующий шаг.",
                )
            else:
                messages.success(
                    request,
                    "Текстовый ввод успешно удален.",
                )
            return redirect("bot-chain", bot_id=bot_id, chain_id=chain_id)

        except Exception as e:
            logger.error(
                f"Failed to turn off/on text input. Chain ID: {chain_id}, Step ID: {step_id}. Error: {str(e)}",
                exc_info=True,
            )
            messages.error(request, f"Ошибка операции: {str(e)}")
            return redirect("bot-chain", bot_id=bot_id, chain_id=chain_id)


class UpdateChainStepView(LoginRequiredMixin, View):
    """View for updating existing chain steps in conversation flows."""

    template_name = "bots_chain/update_chain_step.html"

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


class CreateChainButtonView(LoginRequiredMixin, View):
    """View for creating new chain buttons"""

    def post(
        self, request, bot_id: int, chain_id: int
    ) -> HttpResponseRedirect:
        """
        Handle button creation request

        Args:
            request: HttpRequest object
            bot_id: ID of the bot that owns the chain
            chain_id: ID of the chain

        Returns:
            Redirect to chain view or error page
        """
        bot = get_object_or_404(Bot, id=bot_id)

        if bot.user != request.user:
            raise Http404("You don't have permission to modify this bot.")

        try:
            create_chain_button(
                step_id=int(request.POST.get("step_id")),
                text="<Не задано>",
            )

            messages.success(request, "Кнопка успешно создана.")
            return redirect("bot-chain", bot_id=bot_id, chain_id=chain_id)

        except Exception as e:
            logger.error(
                f"Failed to create chain button. Step ID: {request.POST.get("step_id", "")}. Error: {str(e)}",
                exc_info=True,
            )
            messages.error(request, f"Ошибка при создании кнопки: {str(e)}")
            return redirect("bot-chain", bot_id=bot_id, chain_id=chain_id)


class UpdateChainButtonView(LoginRequiredMixin, View):
    """View for updating existing chain buttons"""

    template_name = "bots_chain/update_chain_button.html"

    def get(
        self, request, bot_id: int, chain_id: int, button_id: int
    ) -> HttpResponse:
        """
        Render step editing form.

        Args:
            request: HttpRequest object
            bot_id: ID of the bot that owns the chain
            chain_id: ID of the chain containing the step
            button_id: ID of the button to edit

        Returns:
            Rendered template with button data

        Raises:
            Http404: If user doesn't own the bot or button not found
        """
        bot = get_object_or_404(Bot, id=bot_id)

        if bot.user != request.user:
            raise Http404("You don't have permission to modify this bot.")

        button = get_chain_button(button_id)
        return render(
            request,
            self.template_name,
            {
                "bot": bot,
                "chain_id": chain_id,
                "button": button,
            },
        )

    def post(
        self, request, bot_id: int, chain_id: int, button_id: int
    ) -> HttpResponseRedirect:
        """
        Handle button update request

        Args:
            request: HttpRequest with updated button data
            bot_id: ID of the bot that owns the chain
            chain_id: ID of the chain
            button_id: ID of the button to update

        Returns:
            Redirect to step edit view
        """
        bot = get_object_or_404(Bot, id=bot_id)

        if bot.user != request.user:
            raise Http404("You don't have permission to modify this bot.")

        try:
            update_chain_button(
                button_id=button_id, text=request.POST.get("text")
            )
            messages.success(request, "Кнопка успешно обновлена.")
            return redirect("bot-chain", bot_id=bot_id, chain_id=chain_id)

        except Exception as e:
            logger.error(
                f"Failed to update chain button. Button ID: {button_id}. Error: {str(e)}",
                exc_info=True,
            )
            messages.error(request, f"Ошибка при обновлении кнопки: {str(e)}")
            return redirect(
                "update-chain-step", bot_id=bot_id, chain_id=chain_id
            )


class DeleteChainButtonView(LoginRequiredMixin, View):
    """View for deleting chain buttons"""

    def post(
        self, request, bot_id: int, chain_id: int, button_id: int
    ) -> HttpResponseRedirect:
        """
        Handle button deletion request

        Args:
            request: HttpRequest object
            bot_id: ID of the bot that owns the chain
            chain_id: ID of the chain
            button_id: ID of the button to delete

        Returns:
            Redirect to step edit view
        """
        bot = get_object_or_404(Bot, id=bot_id)

        if bot.user != request.user:
            raise Http404("You don't have permission to modify this bot.")

        try:
            delete_chain_button(button_id)
            messages.success(request, "Кнопка успешно удалена.")
        except Exception as e:
            logger.error(
                f"Failed to delete chain button. Button ID: {button_id}. Error: {str(e)}",
                exc_info=True,
            )
            messages.error(request, "Ошибка при удалении кнопки.")

        return redirect("bot-chain", bot_id=bot_id, chain_id=chain_id)


class ChainResultsView(LoginRequiredMixin, View):
    """
    View for displaying paginated chain execution results.

    Attributes:
        template_name (str): Path to the template used for rendering.
        RESULTS_PER_PAGE (int): Number of items to display per page.
    """

    template_name = "bots_chain/chain_results.html"
    RESULTS_PER_PAGE = 4

    def get(self, request, bot_id: int, chain_id: int) -> HttpResponse:
        """
        Handle GET request to display chain results.

        Args:
            request: HttpRequest object
            bot_id: ID of the bot
            chain_id: ID of the chain to show results for

        Returns:
            HttpResponse: Rendered template with paginated results

        Raises:
            Http404: If bot doesn't exist or user doesn't have permission
        """
        # Verify bot exists and user has permission
        bot = get_object_or_404(Bot, id=bot_id)
        if bot.user != request.user:
            raise Http404("Permission denied")

        # Get and validate page number from query params
        try:
            page_number = int(request.GET.get("page", 1))
        except ValueError:
            page_number = 1  # Fallback to first page if invalid number

        # Fetch results from API
        results = get_paginated_chain_results(chain_id)
        logger.debug(f"Fetched {len(results)} results for chain {chain_id}")

        # Handle pagination
        if not results:
            page_obj = None  # No results case
        else:
            paginator = Paginator(results, self.RESULTS_PER_PAGE)
            try:
                page_obj = paginator.page(page_number)
            except EmptyPage:
                page_obj = paginator.page(1)  # Fallback to first page

        return render(
            request,
            self.template_name,
            {
                "bot": bot,
                "chain_id": chain_id,
                "page_obj": page_obj,
            },
        )
