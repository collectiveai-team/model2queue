from typing import Callable

from kombu import Queue, Exchange, Connection
from kombu.mixins import ConsumerProducerMixin


class Worker(ConsumerProducerMixin):
    def __init__(self, connection, queue, tgt_exchange, callback_function, routing_key):
        self.connection = connection
        self.queue = queue
        self.tgt_exchange = tgt_exchange
        self.callback_function = callback_function
        self.routing_key = routing_key

    def get_consumers(self, _Consumer, channel):
        return [
            _Consumer(
                queues=self.queue,
                on_message=self.handle_message,
                #  accept="text/plain",
                prefetch_count=10,
            )
        ]

    def handle_message(self, message):
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
