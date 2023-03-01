from typing import Any, List, Callable

from kombu.mixins import ConsumerProducerMixin
from kombu import Message, Consumer, Connection

from model2queue.helper.logger import get_logger

logger = get_logger(__name__)


class ConsumerTaskWorker(ConsumerProducerMixin):
    def __init__(
        self,
        connection: Connection,
        queue: str,
        callback_function: Callable,
    ):
        self.connection = connection
        self.queue = queue
        self.callback_function = callback_function

    def get_consumers(self, consumer: Consumer, channel: Any) -> List[Consumer]:
        return [
            consumer(
                queues=self.queue,
                on_message=self.handle_message,
                prefetch_count=10,
            )
        ]

    def handle_message(self, message: Message) -> None:
        logger.debug(f"received {message} from {self.queue}")
        self.callback_function(message.payload)
