import json
import logging

from bots.models import Bot
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import EmptyPage, Paginator
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from requests.exceptions import RequestException

from .forms import BotChainForm
from .services import ChainButtonService, ChainService, ChainStepService
from .types import ChainButtonData, ChainData, ChainStepData


logger = logging.getLogger("bots")


class BaseChainView(LoginRequiredMixin, View):
    def get_bot_or_404(self, bot_id: int) -> Bot:
        bot = get_object_or_404(Bot, id=bot_id)
        if bot.user != self.request.user:
            raise Http404("You are not the owner of this bot.")
        return bot


class BotChainDetailView(BaseChainView):
    template_name = "bots_chain/chain_details.html"

    def get(self, request, bot_id: int, chain_id: int) -> HttpResponse:
        bot = self.get_bot_or_404(bot_id)

        try:
            chain_data: ChainData = ChainService.get_chain(chain_id)
            chain_json = json.dumps(chain_data, default=str)
            return render(
                request,
                self.template_name,
                {"bot": bot, "chain": chain_data, "chain_json": chain_json},
            )
        except RequestException as e:
            logger.error(f"Failed to fetch chain: {str(e)}", exc_info=True)
            empty_chain: ChainData = {"id": 0, "name": ""}
            return render(
                request,
                self.template_name,
                {"bot": bot, "chain": empty_chain, "chain_json": "{}"},
            )


class BotChainView(BaseChainView):
    template_name = "bots_chain/chains.html"

    def get(self, request, bot_id: int) -> HttpResponse:
        bot = self.get_bot_or_404(bot_id)

        try:
            chains_response = ChainService.get_bot_chains(bot.bot_id)
            return render(
                request,
                self.template_name,
                {"bot": bot, "chains": chains_response.get("chains", [])},
            )
        except RequestException as e:
            logger.error(f"Failed to fetch chains: {str(e)}", exc_info=True)
            return render(
                request,
                self.template_name,
                {"bot": bot, "chains": []},
            )


class CreateChainView(BaseChainView):
    template_name = "bots_chain/create_chain.html"

    def get(self, request, bot_id: int) -> HttpResponse:
        bot = self.get_bot_or_404(bot_id)
        return render(request, self.template_name, {"bot": bot})

    def post(self, request, bot_id: int) -> HttpResponseRedirect:
        bot = self.get_bot_or_404(bot_id)
        form = BotChainForm(request.POST)

        if not form.is_valid():
            messages.error(
                request, "Неверное имя цепочки или имя уже существует."
            )
            return redirect("create-chain", bot_id=bot.id)

        try:
            ChainService.create_chain(bot.bot_id, form.cleaned_data["name"])
            messages.success(request, "Цепочка создана успешно.")
            return redirect("bot-chains", bot_id=bot.id)
        except RequestException as e:
            logger.error(f"Failed to create chain: {str(e)}", exc_info=True)
            messages.error(request, "Ошибка создания цепочки.")
            return redirect("bot-chains", bot_id=bot.id)


class UpdateChainView(BaseChainView):
    def post(
        self, request, bot_id: int, chain_id: int
    ) -> HttpResponseRedirect:
        bot = self.get_bot_or_404(bot_id)
        form = BotChainForm(request.POST)

        if not form.is_valid():
            messages.error(request, "Недопустимое имя цепочки.")
            return redirect("update-chain", bot_id=bot.id, chain_id=chain_id)

        try:
            ChainService.update_chain(chain_id, form.cleaned_data["name"])
            messages.success(request, "Цепочка успешно обновлена.")
            return redirect("bot-chain", bot_id=bot.id, chain_id=chain_id)
        except RequestException as e:
            logger.error(f"Failed to update chain: {str(e)}", exc_info=True)
            messages.error(request, "Ошибка обновления цепочки.")
            return redirect("update-chain", bot_id=bot.id, chain_id=chain_id)


class DeleteChainView(BaseChainView):
    def post(
        self, request, bot_id: int, chain_id: int
    ) -> HttpResponseRedirect:
        self.get_bot_or_404(bot_id)

        try:
            ChainService.delete_chain(chain_id)
            messages.success(request, "Цепочка успешно удалена.")
        except RequestException as e:
            logger.error(f"Failed to delete chain: {str(e)}", exc_info=True)
            messages.error(request, "Ошибка удаления цепочки.")

        return redirect("bot-chains", bot_id=bot_id)


class ChainStepMixin(BaseChainView):
    def get_step_data(self, step_id: int) -> ChainStepData:
        try:
            return ChainStepService.get_step(step_id)
        except RequestException as e:
            logger.error(f"Failed to get step {step_id}: {str(e)}")
            raise Http404("Step not found")


class CreateChainStepView(ChainStepMixin):
    def post(
        self, request, bot_id: int, chain_id: int
    ) -> HttpResponseRedirect:
        self.get_bot_or_404(bot_id)

        try:
            ChainStepService.create_step(
                chain_id=chain_id,
                name="<Не задано>",
                message="<Не задано>",
                button_id=request.POST.get("set_as_next_step_for_button_id"),
            )
            messages.success(request, "Шаг успешно создан.")
        except RequestException as e:
            logger.error(f"Failed to create step: {str(e)}", exc_info=True)
            messages.error(request, "Ошибка создания шага.")

        return redirect("bot-chain", bot_id=bot_id, chain_id=chain_id)


class CreateChainStepTextinputView(ChainStepMixin):
    def post(
        self, request, bot_id: int, chain_id: int
    ) -> HttpResponseRedirect:
        self.get_bot_or_404(bot_id)

        try:
            response = ChainStepService.create_step(
                chain_id=chain_id, name="<Не задано>", message="<Не задано>"
            )

            ChainStepService.update_step(
                step_id=int(request.POST.get("set_as_next_step_for_step_id")),
                next_step_id=int(response["id"]),
            )

            messages.success(
                request, "Шаг для текстового ввода успешно создан."
            )
        except RequestException as e:
            logger.error(
                f"Failed to create textinput step: {str(e)}", exc_info=True
            )
            messages.error(
                request, "Ошибка создания шага для текстового ввода."
            )

        return redirect("bot-chain", bot_id=bot_id, chain_id=chain_id)


class UpdateChainStepView(ChainStepMixin):
    template_name = "bots_chain/update_chain_step.html"

    def get(
        self, request, bot_id: int, chain_id: int, step_id: int
    ) -> HttpResponse:
        bot = self.get_bot_or_404(bot_id)
        step = self.get_step_data(step_id)

        return render(
            request,
            self.template_name,
            {"bot": bot, "chain_id": chain_id, "step": step},
        )

    def post(
        self, request, bot_id: int, chain_id: int, step_id: int
    ) -> HttpResponseRedirect:
        self.get_bot_or_404(bot_id)

        try:
            ChainStepService.update_step(
                step_id=step_id,
                name=request.POST.get("name"),
                message=request.POST.get("message"),
            )
            messages.success(request, "Шаг успешно обновлен.")
        except RequestException as e:
            logger.error(f"Failed to update step: {str(e)}", exc_info=True)
            messages.error(request, "Ошибка обновления шага.")

        return redirect("bot-chain", bot_id=bot_id, chain_id=chain_id)


class DeleteChainStepView(ChainStepMixin):
    def post(
        self, request, bot_id: int, chain_id: int, step_id: int
    ) -> HttpResponseRedirect:
        self.get_bot_or_404(bot_id)

        try:
            ChainStepService.delete_step(step_id)
            messages.success(request, "Шаг успешно удален.")
        except RequestException as e:
            logger.error(f"Failed to delete step: {str(e)}", exc_info=True)
            messages.error(request, "Ошибка удаления шага.")

        return redirect("bot-chain", bot_id=bot_id, chain_id=chain_id)


class EditTextinputView(ChainStepMixin):
    def post(
        self, request, bot_id: int, chain_id: int, step_id: int
    ) -> HttpResponseRedirect:
        self.get_bot_or_404(bot_id)
        text_input = request.POST.get("text_input") == "on"

        try:
            ChainStepService.update_step(
                step_id=int(step_id), text_input=text_input
            )

            if text_input:
                messages.success(request, "Текстовый ввод включен.")
            else:
                messages.success(request, "Текстовый ввод отключен.")
        except RequestException as e:
            logger.error(
                f"Failed to update text input: {str(e)}", exc_info=True
            )
            messages.error(
                request, "Ошибка обновления настроек текстового ввода."
            )

        return redirect("bot-chain", bot_id=bot_id, chain_id=chain_id)


class ChainButtonMixin(BaseChainView):
    def get_button_data(self, button_id: int) -> ChainButtonData:
        try:
            return ChainButtonService.get_button(button_id)
        except RequestException as e:
            logger.error(f"Failed to get button {button_id}: {str(e)}")
            raise Http404("Button not found")


class CreateChainButtonView(ChainButtonMixin):
    def post(
        self, request, bot_id: int, chain_id: int
    ) -> HttpResponseRedirect:
        self.get_bot_or_404(bot_id)

        try:
            ChainButtonService.create_button(
                step_id=int(request.POST.get("step_id")), text="<Не задано>"
            )
            messages.success(request, "Кнопка успешно создана.")
        except RequestException as e:
            logger.error(f"Failed to create button: {str(e)}", exc_info=True)
            messages.error(request, "Ошибка создания кнопки.")

        return redirect("bot-chain", bot_id=bot_id, chain_id=chain_id)


class UpdateChainButtonView(ChainButtonMixin):
    template_name = "bots_chain/update_chain_button.html"

    def get(
        self, request, bot_id: int, chain_id: int, button_id: int
    ) -> HttpResponse:
        bot = self.get_bot_or_404(bot_id)
        button = self.get_button_data(button_id)

        return render(
            request,
            self.template_name,
            {"bot": bot, "chain_id": chain_id, "button": button},
        )

    def post(
        self, request, bot_id: int, chain_id: int, button_id: int
    ) -> HttpResponseRedirect:
        self.get_bot_or_404(bot_id)

        try:
            ChainButtonService.update_button(
                button_id=button_id, text=request.POST.get("text")
            )
            messages.success(request, "Кнопка успешно обновлена.")
        except RequestException as e:
            logger.error(f"Failed to update button: {str(e)}", exc_info=True)
            messages.error(request, "Ошибка обновления кнопки.")

        return redirect("bot-chain", bot_id=bot_id, chain_id=chain_id)


class DeleteChainButtonView(ChainButtonMixin):
    def post(
        self, request, bot_id: int, chain_id: int, button_id: int
    ) -> HttpResponseRedirect:
        self.get_bot_or_404(bot_id)

        try:
            ChainButtonService.delete_button(button_id)
            messages.success(request, "Кнопка успешно удалена.")
        except RequestException as e:
            logger.error(f"Failed to delete button: {str(e)}", exc_info=True)
            messages.error(request, "Ошибка удаления кнопки.")

        return redirect("bot-chain", bot_id=bot_id, chain_id=chain_id)


class ChainResultsView(BaseChainView):
    template_name = "bots_chain/chain_results.html"
    RESULTS_PER_PAGE = 4

    def get(self, request, bot_id: int, chain_id: int) -> HttpResponse:
        bot = self.get_bot_or_404(bot_id)

        try:
            page_number = int(request.GET.get("page", 1))
        except ValueError:
            page_number = 1

        results = ChainService.get_chain_results(chain_id)
        paginator = Paginator(results, self.RESULTS_PER_PAGE)

        try:
            page_obj = paginator.page(page_number)
        except EmptyPage:
            page_obj = paginator.page(1)

        return render(
            request,
            self.template_name,
            {"bot": bot, "chain_id": chain_id, "page_obj": page_obj},
        )
