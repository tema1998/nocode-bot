from typing import Dict, Literal

from bot_service.services.mailing_service import (
    MailingService,
    get_mailing_service,
)
from fastapi import APIRouter, Depends


router = APIRouter(prefix="/mailings", tags=["mailings"])


@router.post(
    "/{bot_id}/start",
    response_model=Dict[str, str | int],
    summary="Start new mailing campaign",
    response_description="Initial mailing status with tracking ID",
    status_code=202,
)
async def start_mailing(
    bot_id: int,
    message: str,
    mailing_service: MailingService = Depends(get_mailing_service),
) -> Dict[str, str | int]:
    """
    Initiates a new mailing campaign to all users of specified bot.

    Args:
        bot_id (int): ID of the bot whose users will receive the message
        message (str): Content to be broadcasted to users
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
    return await mailing_service.create_mailing(bot_id, message)


@router.get(
    "/{mailing_id}/status",
    response_model=Dict[str, str | Dict],
    summary="Check mailing status",
    response_description="Current status of mailing campaign",
)
async def get_status(
    mailing_id: int,
    mailing_service: MailingService = Depends(get_mailing_service),
) -> Dict[str, str | Dict]:
    """
    Retrieves current status of an ongoing or completed mailing campaign.

    Args:
        mailing_id (int): ID of mailing campaign to check
        mailing_service (MailingService): Injected mailing service dependency

    Returns:
        Dict[str, str | Dict]: Status dictionary with one of these structures:
            - {"status": "not_found"}
            - {"status": "in_progress"}
            - {"status": "completed", "result": {stats_dict}}
            - {"status": "failed", "error": error_message}

    Note:
        The 'result' field for completed mailings contains delivery statistics
        including total users, successful deliveries, and failures.
    """
    return await mailing_service.get_mailing_status(mailing_id)


@router.post(
    "/{mailing_id}/cancel",
    response_model=Dict[str, Literal["cancelled", "not_cancelled"]],
    summary="Cancel active mailing",
    response_description="Cancellation attempt result",
)
async def cancel_mailing(
    mailing_id: int,
    mailing_service: MailingService = Depends(get_mailing_service),
) -> Dict[str, Literal["cancelled", "not_cancelled"]]:
    """
    Attempts to cancel an active mailing campaign.

    Args:
        mailing_id (int): ID of mailing campaign to cancel
        mailing_service (MailingService): Injected mailing service dependency

    Returns:
        Dict[str, Literal["cancelled", "not_cancelled"]]:
            {"status": "cancelled"} if successful,
            {"status": "not_cancelled"} if mailing couldn't be cancelled

    Note:
        Only mailings with "in_progress" status can be cancelled.
        Completed or failed mailings will return "not_cancelled".
    """
    success = await mailing_service.cancel_mailing(mailing_id)
    return {"status": "cancelled" if success else "not_cancelled"}
