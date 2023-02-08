from threading import Thread

from fastapi import FastAPI
from kombu import Queue, Exchange, Producer, Connection

from model2queue.workers import start_consumer_producer


def predict_from_queue(func, conn_url: str = "memory://localhost/"):
    connection = Connection(conn_url)

    in_exchange = Exchange("in_excahnge", type="direct")
    in_queue = Queue(name="queue1", exchange=in_exchange, routing_key="api_model_input")
    in_queue.maybe_bind(connection)
    in_queue.declare()

    out_exchange = Exchange("out_exchange", type="direct")
    out_queue = Queue(
        name="out_queue", exchange=out_exchange, routing_key="api_model_output"
    )
    out_queue.maybe_bind(connection)
    out_queue.declare()

    def func_wrapper(*args, **kwargs):
        output = func(*args, **kwargs)
        print("postprocess")
        return output

    model_input_reader = Thread(
        target=start_consumer_producer,
        kwargs={
            "connection": connection,
            "queue": in_queue,
            "tgt_exchange": out_exchange,
            "callback_function": func_wrapper,
            "routing_key": "api_model_output",
        },
    )
    model_input_reader.start()


def enqueue_task(conn_url: str = "memory://localhost/"):
    connection = Connection(conn_url)
    channel = connection.channel()

    in_exchange = Exchange("in_excahnge", type="direct")
    in_queue = Queue(name="queue1", exchange=in_exchange, routing_key="api_model_input")
    in_queue.maybe_bind(connection)
    in_queue.declare()

    out_exchange = Exchange("out_exchange", type="direct")
    out_queue = Queue(
        name="out_queue", exchange=out_exchange, routing_key="api_model_output"
    )
    out_queue.maybe_bind(connection)
    out_queue.declare()

    producer = Producer(
        exchange=in_exchange, channel=channel, routing_key="api_model_input"
    )

    app = FastAPI()

    @app.post("/task")
    async def create_item(task: dict) -> dict:

        producer.publish(task)
        return {"status": "ok"}

    app.run()
