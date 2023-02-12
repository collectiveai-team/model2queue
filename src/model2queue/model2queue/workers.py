from typing import Any, List, Callable

from kombu.mixins import ConsumerProducerMixin
from kombu import Queue, Message, Consumer, Exchange, Connection


class Worker(ConsumerProducerMixin):
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
                #  accept="text/plain",
                prefetch_count=10,
            )
        ]

    def handle_message(self, message: Message) -> None:
        print(message)
        self.producer.publish(
            "hello to you",
            exchange=self.tgt_exchange,
            routing_key=self.routing_key,
            retry=True,
        )
        print("publishing: hello to you")


def start_consumer_producer(
    connection: Connection,
    queue: Queue,
    tgt_exchange: Exchange,
    callback_function: Callable[[str], None],
    routing_key: str,
):
    queue.maybe_bind(connection)
    queue.declare()
    worker = Worker(
        connection=connection,
        queue=queue,
        tgt_exchange=tgt_exchange,
        callback_function=callback_function,
        routing_key=routing_key,
    )
    worker.run()
