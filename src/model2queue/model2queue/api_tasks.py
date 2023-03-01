import functools
from typing import Union, Callable

from kombu import Queue, Exchange, Producer, Connection

from model2queue.helper.logger import get_logger
from model2queue.workers import (
    WorkerThread,
    ConsumerTaskWorker,
    ConsumerProducerTaskWorker,
)

logger = get_logger(__name__)


def start_worker(worker: Union[ConsumerTaskWorker, ConsumerProducerTaskWorker]):
    worker.run()


def start_consumer_producer(
    connection: Connection,
    queue: Queue,
    tgt_exchange: Exchange,
    callback_function: Callable[[str], None],
    routing_key: str,
):
    queue.maybe_bind(connection)
    queue.declare()
    worker = ConsumerProducerTaskWorker(
        connection=connection,
        queue=queue,
        tgt_exchange=tgt_exchange,
        callback_function=callback_function,
        routing_key=routing_key,
    )
    worker.run()


def start_consumer(
    connection: Connection,
    queue: Queue,
    callback_function: Callable[[str], None],
):
    queue.maybe_bind(connection)
    queue.declare()
    worker = ConsumerTaskWorker(
        connection=connection,
        queue=queue,
        callback_function=callback_function,
    )
    worker.run()


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

    worker = ConsumerProducerTaskWorker(
        connection=connection,
        queue=in_queue,
        tgt_exchange=out_exchange,
        callback_function=func,
        routing_key=out_routing_key,
    )

    model_input_reader = WorkerThread(
        worker=worker,
        target=start_worker,
        kwargs={
            "worker": worker,
        },
    )
    model_input_reader.start()
    return model_input_reader


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

    worker = ConsumerTaskWorker(
        connection=connection,
        queue=in_queue,
        callback_function=func,
    )

    model_input_reader = WorkerThread(
        worker=worker,
        target=start_worker,
        kwargs={
            "worker": worker,
        },
    )
    model_input_reader.start()
    return model_input_reader


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
