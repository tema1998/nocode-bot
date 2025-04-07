from bot_service.services.webhook_service import (
    WebhookService,
    get_webhook_service,
)
from fastapi import APIRouter, Depends


router = APIRouter()


@router.post(
    "/{bot_id}",
    summary="Handle incoming webhook update",
    description="Processes incoming updates from a bot's webhook, managing user state and funnel steps.",
    response_description="Webhook handling status",
    status_code=200,
)
async def webhook(
    bot_id: int,
    update_data: dict,
    webhook_service: WebhookService = Depends(get_webhook_service),
):
    """
    Handle incoming webhook updates.

    Args:
        bot_id (int): The ID of the bot.
        update_data (dict): The incoming update data from Telegram.
        webhook_service (WebhookService): The service to handle incoming webhook update.

    Returns:
        dict: A status message indicating the result of the operation.
    """
    return await webhook_service.handle_webhook(bot_id, update_data)
