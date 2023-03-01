from typing import Any, List, Callable

from kombu.mixins import ConsumerProducerMixin
from kombu import Message, Consumer, Connection

from model2queue.helper.logger import get_logger

logger = get_logger(__name__)


class ConsumerProducerTaskWorker(ConsumerProducerMixin):
    def __init__(
        self,
        connection: Connection,
        queue: str,
        tgt_exchange: str,
        callback_function: Callable,
        routing_key: str,
    ):
        self.connection = connection
        self.queue = queue
        self.tgt_exchange = tgt_exchange
        self.callback_function = callback_function
        self.routing_key = routing_key

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
        output = self.callback_function(message.payload)
        self.producer.publish(
            output,
            exchange=self.tgt_exchange,
            routing_key=self.routing_key,
            retry=True,
        )
        logger.debug(f"published {output} to {self.tgt_exchange}")
