from typing import Dict

from bot_service.schemas.bot import MailingRequest
from bot_service.services.mailing_service import (
    MailingService,
    get_mailing_service,
)
from fastapi import APIRouter, Depends


router = APIRouter()


@router.post(
    "/{bot_id}/start/",
    response_model=Dict[str, str | int],
    summary="Start new mailing campaign",
    response_description="Initial mailing status with tracking ID",
    status_code=202,
)
async def start_mailing(
    bot_id: int,
    message_request: MailingRequest,
    mailing_service: MailingService = Depends(get_mailing_service),
) -> Dict[str, str | int]:
    """
    Initiates a new mailing campaign to all users of specified bot.

    Args:
        bot_id (int): ID of the bot whose users will receive the message
        message_request (MailingRequest): Message text
        mailing_service (MailingService): Injected mailing service dependency

    Returns:
        Dict[str, str | int]: Dictionary containing:
            - mailing_id: Unique identifier for tracking status
            - status: Initial status ("started")
            - started_at: ISO timestamp of initiation
            - bot_id: Echo of input bot_id

    Raises:
        HTTPException 404: If specified bot doesn't exist
        HTTPException 500: If internal processing fails
    """
    return await mailing_service.create_mailing(
        bot_id, message_request.message
    )
