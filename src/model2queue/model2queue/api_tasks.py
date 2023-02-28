import functools
from typing import Callable
from threading import Thread

from kombu import Queue, Exchange, Producer, Connection

from model2queue.helper.logger import get_logger
from model2queue.workers import start_consumer, start_consumer_producer

logger = get_logger(__name__)


def start_api_task_consumer_producer(
    func: Callable,
    conn_url: str = "memory://localhost/",
    in_queue_name: str = "queue_in",
    in_exchange_name: str = "in_excahnge",
    in_routing_key: str = "api_model_input",
    out_queue_name: str = "queue_in",
    out_exchange_name: str = "out_exchange",
    out_routing_key: str = "api_model_output",
) -> None:
    connection = Connection(conn_url)

    in_exchange = Exchange(in_exchange_name, type="direct")
    in_queue = Queue(
        name=in_queue_name, exchange=in_exchange, routing_key=in_routing_key
    )
    in_queue.maybe_bind(connection)
    in_queue.declare()

    out_exchange = Exchange(out_exchange_name, type="direct")
    out_queue = Queue(
        name=out_queue_name, exchange=out_exchange, routing_key=out_routing_key
    )
    out_queue.maybe_bind(connection)
    out_queue.declare()

    model_input_reader = Thread(
        target=start_consumer_producer,
        kwargs={
            "connection": connection,
            "queue": in_queue,
            "tgt_exchange": out_exchange,
            "callback_function": func,
            "routing_key": "api_model_output",
        },
    )
    model_input_reader.start()


def start_api_task_consumer(
    func: Callable,
    conn_url: str = "memory://localhost/",
    in_queue_name: str = "queue_in",
    in_exchange_name: str = "in_excahnge",
    routing_key: str = "api_model_input",
) -> None:
    connection = Connection(conn_url)

    in_exchange = Exchange(in_exchange_name, type="direct")
    in_queue = Queue(name=in_queue_name, exchange=in_exchange, routing_key=routing_key)
    in_queue.maybe_bind(connection)
    in_queue.declare()

    model_input_reader = Thread(
        target=start_consumer,
        kwargs={
            "connection": connection,
            "queue": in_queue,
            "callback_function": func,
        },
    )
    model_input_reader.start()


def api_task_producer(
    conn_url: str = "memory://localhost/",
    in_queue_name: str = "queue_in",
    in_exchange_name: str = "in_excahnge",
    in_routing_key: str = "api_model_input",
):
    connection = Connection(conn_url)
    channel = connection.channel()

    in_exchange = Exchange(in_exchange_name, type="direct")
    in_queue = Queue(
        name=in_queue_name, exchange=in_exchange, routing_key=in_routing_key
    )
    in_queue.maybe_bind(connection)
    in_queue.declare()

    producer = Producer(
        exchange=in_exchange, channel=channel, routing_key=in_routing_key
    )

    def api_task_producer_outer(func: Callable):
        @functools.wraps(func)
        def func_wrapper(*args, **kwargs):
            output = func(*args, **kwargs)
            producer.publish(output)
            return output

        return func_wrapper

    return api_task_producer_outer
