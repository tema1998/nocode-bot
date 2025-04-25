import abc
import json
import logging
from typing import Any, Dict, Optional

import aio_pika
from aio_pika.abc import AbstractRobustConnection


logger = logging.getLogger(__name__)


class MessageBrokerRepository(abc.ABC):
    """Abstract base class for message broker operations."""

    @abc.abstractmethod
    async def publish(self, queue_name: str, message: Dict[str, Any]) -> bool:
        """Publish message to queue."""
        pass

    @abc.abstractmethod
    async def consume(self, queue_name: str, callback) -> None:
        """Start consuming messages from queue."""
        pass


class RabbitMQRepository(MessageBrokerRepository):
    """RabbitMQ implementation of MessageBrokerRepository."""

    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.connection: Optional[AbstractRobustConnection] = None
        self.channel = None

    async def connect(self) -> None:
        """Establish connection to RabbitMQ."""
        if not self.connection or self.connection.is_closed:
            self.connection = await aio_pika.connect_robust(
                self.connection_string
            )
            self.channel = await self.connection.channel()  # type: ignore

    async def close(self) -> None:
        """Close connection."""
        if self.connection:
            await self.connection.close()

    async def publish(self, queue_name: str, message: Dict[str, Any]) -> bool:
        """Publish message to RabbitMQ queue."""
        try:
            await self.connect()
            queue = await self.channel.declare_queue(queue_name, durable=True)  # type: ignore
            await self.channel.default_exchange.publish(  # type: ignore
                aio_pika.Message(body=json.dumps(message).encode()),
                routing_key=queue.name,
            )
            return True
        except Exception as e:
            logger.error(f"Failed to publish message: {str(e)}")
            return False

    async def consume(self, queue_name: str, callback) -> None:
        """Start consuming messages from RabbitMQ queue."""
        await self.connect()
        queue = await self.channel.declare_queue(queue_name, durable=True)  # type: ignore

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    try:
                        payload = json.loads(message.body.decode())
                        await callback(payload)
                    except Exception as e:
                        logger.error(f"Error processing message: {str(e)}")
