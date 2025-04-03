import logging
from typing import Any, Dict, Optional

from bot_service.models import Chain
from bot_service.models.main_menu import Button, MainMenu
from bot_service.repositories.async_pg_repository import (
    PostgresAsyncRepository,
    get_repository,
)
from bot_service.repositories.telegram_api_repository import (
    TelegramApiRepository,
    get_telegram_api_repository,
)
from bot_service.schemas.main_menu import (
    ButtonResponse,
    ButtonUpdateResponse,
    PatchWelcomeMessageResponse,
)
from bot_service.services.mailing_service import (
    MailingService,
    get_mailing_service,
)
from fastapi import Depends, HTTPException, status


logger = logging.getLogger(__name__)


class MainMenuService:
    """
    Service for managing the main menu of a bot, including database and Telegram API interactions.
    """

    def __init__(
        self,
        db_repository: PostgresAsyncRepository,
        tg_api_repository: TelegramApiRepository,
        mailing_service: MailingService,
    ) -> None:
        """
        Initialize the MainMenuService.

        Args:
            db_repository (PostgresAsyncRepository): The repository for database operations.
            tg_api_repository (TelegramApiRepository): The repository for Telegram API interactions.
        """
        self.db_repository = db_repository
        self.tg_api_repository = tg_api_repository
        self.mailing_service = mailing_service

    async def _get_main_menu(self, bot_id: int) -> MainMenu:
        """Internal method to get main menu or raise 404 if not found."""
        main_menu = await self.db_repository.fetch_by_query_one_joinedload(
            MainMenu, {"bot_id": bot_id}, "buttons"
        )
        if main_menu is None:
            logger.error(f"Bot with ID {bot_id} doesn't have a main menu.")
            raise HTTPException(
                status_code=404, detail="Bot's main menu not found"
            )
        return main_menu  # type: ignore

    async def _get_button(self, button_id: int) -> Button:
        """Internal method to get button or raise 404 if not found."""
        button = await self.db_repository.fetch_by_query_one_joinedload(
            Button, {"id": button_id}
        )
        if button is None:
            logger.error(f"Button with ID {button_id} not found.")
            raise HTTPException(status_code=404, detail="Button not found")
        return button  # type: ignore

    async def _process_chain_association(
        self, button: Button, chain_id: Optional[int]
    ) -> None:
        """Internal method to handle chain association logic."""
        if chain_id is not None:
            try:
                chain = await self.db_repository.fetch_by_id(Chain, chain_id)
                if chain and chain.bot_id == button.bot_id:
                    button.chain_id = chain_id  # type: ignore
                else:
                    logger.error(f"Failed to set chain with ID={chain_id}")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Failed to set chain to button",
                    )
            except Exception as e:
                logger.error(f"Failed to update chain association: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update chain association",
                )
        else:
            button.chain_id = None  # type: ignore

    async def main_menu_with_welcome_message(
        self, bot_id: int
    ) -> Dict[str, Any]:
        """
        Retrieve the main menu and its welcome message for a specific bot.

        Args:
            bot_id (int): The unique identifier of the bot.

        Returns:
            Dict[str, Any]: A dictionary containing the welcome message and a list of buttons.

        Raises:
            HTTPException: If the main menu for the specified bot ID is not found.
        """
        main_menu = await self._get_main_menu(bot_id)

        return {
            "welcome_message": main_menu.welcome_message,  # type: ignore
            "buttons": [
                ButtonResponse(
                    id=button.id,  # type: ignore
                    bot_id=bot_id,
                    button_text=button.button_text,  # type: ignore
                    reply_text=button.reply_text,  # type: ignore
                )
                for button in main_menu.buttons  # type: ignore
            ],
        }

    async def update_welcome_message(
        self, bot_id: int, welcome_message: str
    ) -> PatchWelcomeMessageResponse:
        """
        Update the welcome message of the main menu for a specific bot.

        Args:
            bot_id (int): The unique identifier of the bot.
            welcome_message (str): The new welcome message to set.

        Raises:
            HTTPException: If the main menu for the specified bot ID is not found.
        """
        main_menu = await self._get_main_menu(bot_id)
        main_menu.welcome_message = welcome_message  # type: ignore
        await self.db_repository.update(main_menu)

        return PatchWelcomeMessageResponse(
            bot_id=bot_id, welcome_message=welcome_message
        )

    async def get_main_menu_button(self, button_id: int) -> ButtonResponse:
        """
        Retrieve the details of a specific button by its ID.

        Args:
            button_id (int): The unique identifier of the button to retrieve.

        Returns:
            ButtonResponse: A response model containing the details of the button.

        Raises:
            HTTPException:
                - 404: If the button with the specified ID is not found.
        """
        button = await self._get_button(button_id)
        chain = None

        if button.chain_id:  # type: ignore
            chain = await self.db_repository.fetch_by_query_one_joinedload(
                Chain, {"id": button.chain_id}  # type: ignore
            )

        response = ButtonResponse(
            id=button.id,  # type: ignore
            bot_id=button.bot_id,  # type: ignore
            button_text=button.button_text,  # type: ignore
            reply_text=button.reply_text,  # type: ignore
        )
        if chain:
            response.chain_id = chain.id  # type: ignore
            response.chain = chain.name  # type: ignore
        return response

    async def create_main_menu_button(
        self,
        bot_id: int,
        button_text: str,
        reply_text: str,
        chain_id: Optional[int] = None,
    ) -> ButtonResponse:
        """
        Create a new button for the main menu of a specific bot.

        Args:
            bot_id (int): The unique identifier of the bot to which the button belongs.
            button_text (str): The text displayed on the button.
            reply_text (str): The text sent as a reply when the button is clicked.
            chain_id (Optional[int]): Button starts chain with ID = chain_id.

        Returns:
            ButtonResponse: A response model containing the details of the created button.

        Raises:
            HTTPException: If the main menu for the specified bot ID is not found.
        """
        main_menu = await self._get_main_menu(bot_id)
        await self._check_button_text_constraint(bot_id, button_text)

        button = Button(
            button_text=button_text,
            reply_text=reply_text,
            main_menu_id=main_menu.id,  # type: ignore
            bot_id=bot_id,
        )

        await self._process_chain_association(button, chain_id)
        await self.db_repository.insert(button)

        # Send notification to users that buttons were updated
        await self.mailing_service.create_mailing(
            bot_id,
            "В кнопки главного меню внесены изменения. Чтобы обновить ваше главное меню: нажмите /update",
        )
        return ButtonResponse(
            id=button.id,  # type: ignore
            bot_id=bot_id,
            button_text=button_text,
            reply_text=reply_text,
        )

    async def update_main_menu_button(
        self,
        button_id: int,
        button_text: str,
        reply_text: str,
        chain_id: Optional[int] = None,
    ) -> ButtonUpdateResponse:
        """
        Update the text and reply text of a button in the main menu.

        Args:
            button_id (int): The unique identifier of the button to update.
            button_text (str): The new text to display on the button.
            reply_text (str): The new text to send as a reply when the button is clicked.
            chain_id (Optional[int]): The button starts chain with ID = chain_id.

        Returns:
            ButtonUpdateResponse: A response model containing the details of the updated button.

        Raises:
            HTTPException:
                - 404: If the button with the specified ID is not found.
                - 400: If a button with the same text already exists for the same bot.
        """
        button = await self._get_button(button_id)

        if button_text != button.button_text:  # type: ignore
            await self._check_button_text_constraint(
                button.bot_id, button_text  # type: ignore
            )

        button.button_text = button_text  # type: ignore
        button.reply_text = reply_text  # type: ignore

        await self._process_chain_association(button, chain_id)
        await self.db_repository.update(button)
        # Send notification to users that buttons were updated
        await self.mailing_service.create_mailing(
            int(button.bot_id),
            "В кнопки главного меню внесены изменения. Чтобы обновить ваше главное меню: нажмите /update",
        )

        return ButtonUpdateResponse(
            id=button.id,  # type: ignore
            bot_id=button.bot_id,  # type: ignore
            button_text=button.button_text,  # type: ignore
            reply_text=button.reply_text,  # type: ignore
        )

    async def delete_main_menu_button(self, button_id: int) -> None:
        """
        Delete a button from the main menu.

        Args:
            button_id (int): The unique identifier of the button to delete.

        Raises:
            HTTPException:
                - 404: If the button with the specified ID is not found.
        """
        button = await self._get_button(button_id)
        await self.db_repository.delete(Button, button.id)  # type: ignore
        # Send notification to users that buttons were updated
        await self.mailing_service.create_mailing(
            int(button.bot_id),
            "В кнопки главного меню внесены изменения. Чтобы обновить ваше главное меню: нажмите /update",
        )

    async def _check_button_text_constraint(self, bot_id, button_text):
        buttons_with_same_text = await self.db_repository.fetch_by_query(
            Button, {"bot_id": bot_id, "button_text": button_text}
        )
        if buttons_with_same_text:
            raise HTTPException(
                status_code=400,
                detail="A button with the same text already exists.",
            )
        if button_text == "/start" or button_text == "/update":
            raise HTTPException(
                status_code=400,
                detail="A button with this name is forbidden.",
            )


def get_main_menu_service(
    db_repository: PostgresAsyncRepository = Depends(get_repository),
    tg_api_repository: TelegramApiRepository = Depends(
        get_telegram_api_repository,
    ),
    mailing_service: MailingService = Depends(get_mailing_service),
) -> MainMenuService:
    """
    Dependency function to get an instance of MainMenuService.

    Args:
        db_repository (PostgresAsyncRepository): The repository for database operations.
        tg_api_repository (TelegramApiRepository): The repository for Telegram API interactions.
        mailing_service (MailingService): The mailing service.

    Returns:
        MainMenuService: An instance of MainMenuService.
    """
    return MainMenuService(db_repository, tg_api_repository, mailing_service)
