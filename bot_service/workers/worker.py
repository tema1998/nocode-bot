import asyncio
import logging

from bot_service.workers.mailing_worker import MailingWorker


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    worker = MailingWorker()
    try:
        await worker.start()
    except KeyboardInterrupt:
        await worker.stop()
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        await worker.stop()
        raise


if __name__ == "__main__":
    asyncio.run(main())
