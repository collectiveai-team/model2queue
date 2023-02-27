import functools
import multiprocessing
from typing import Callable
from threading import Thread

import uvicorn
from fastapi import FastAPI, Request
from kombu import Queue, Exchange, Producer, Connection

from model2queue.logger import get_logger
from model2queue.workers import start_consumer, start_consumer_producer

logger = get_logger(__name__)


class UvicornServer(multiprocessing.Process):
    def __init__(self, config: uvicorn.Config):
        super().__init__()

        self.config = config

    def stop(self):
        self.terminate()

    def run(self, *args, **kwargs):
        server = uvicorn.Server(config=self.config)
        server.run()


def api_task_consumer_producer(
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

    @functools.wraps(func)
    def func_wrapper(*args, **kwargs):
        output = func(*args, **kwargs)
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


# def somedec(somearg, someopt=None):
#     def somedec_outer(fn):
#         @wraps(fn)
#         def somedec_inner(*args, **kwargs):
#             # do stuff with somearg, someopt, args and kwargs
#             response = fn(*args, **kwargs)
#             return response

#         return somedec_inner

#     return somedec_outer


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

    # def func_wrapper(*args, **kwargs):
    #     output = func(*args, **kwargs)
    #     return output

    # def api_task_consumer_outer(func: Callable):
    #     @functools.wraps(func)
    #     def func_wrapper(*args, **kwargs):
    #         output = func(*args, **kwargs)
    #         return output

    #     return func_wrapper

    model_input_reader = Thread(
        target=start_consumer,
        kwargs={
            "connection": connection,
            "queue": in_queue,
            "callback_function": func,
        },
    )
    model_input_reader.start()
    # return api_task_consumer_outer


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


# def api_task_producer(
#     func: Callable,
#     conn_url: str = "memory://localhost/",
#     api_host: str = "127.0.0.1",
#     api_port: int = 8000,
#     in_queue_name: str = "queue_in",
#     in_exchange_name: str = "in_excahnge",
#     in_routing_key: str = "api_model_input",
# ):
#     connection = Connection(conn_url)
#     channel = connection.channel()

#     in_exchange = Exchange(in_exchange_name, type="direct")
#     in_queue = Queue(
#         name=in_queue_name, exchange=in_exchange, routing_key=in_routing_key
#     )
#     in_queue.maybe_bind(connection)
#     in_queue.declare()

#     producer = Producer(
#         exchange=in_exchange, channel=channel, routing_key=in_routing_key
#     )

#     app = FastAPI()

#     @app.get("/")
#     async def docs_redirect():
#         return RedirectResponse(url="/docs")

#     from inspect import signature

#     sig = signature(func)
#     arguments = [f"{s.name}: {s.annotation.__name__}" for s in sig.parameters.values()]
#     # f2 = make_fun()

#     # def make_fun(parameters, return_annotation):
#     #     exec(
#     #         "def f_make_fun({}) -> {}: pass".format(
#     #             ", ".join(parameters), return_annotation
#     #         )
#     #     )
#     #     return locals()["f_make_fun"]

#     @app.post(f"/{func.__name__}")
#     def create_task(*arguments) -> sig.return_annotation:
#         task = func(*arguments)
#         producer.publish(task)
#         return {"status": "ok"}

#     config = uvicorn.Config(app=app, host=api_host, port=api_port, log_level="info")
#     server = UvicornServer(config)

#     run_in_main_loop(server.run)

#     logger.info(f"running on {config.host}:{config.port}")


class ProducerMiddleware:
    def __init__(
        self,
        conn_url: str = "memory://localhost/",
        in_queue_name: str = "queue_in",
        in_exchange_name: str = "in_excahnge",
        in_routing_key: str = "api_model_input",
    ):

        self.connection = Connection(conn_url)
        self.channel = self.connection.channel()

        self.in_exchange = Exchange(in_exchange_name, type="direct")
        self.in_queue = Queue(
            name=in_queue_name, exchange=self.in_exchange, routing_key=in_routing_key
        )
        self.in_queue.maybe_bind(self.connection)
        self.in_queue.declare()

        self.producer = Producer(
            exchange=self.in_exchange, channel=self.channel, routing_key=in_routing_key
        )

    async def __call__(self, request: Request, call_next):

        response = await call_next(request)
        self.producer.publish(response)
        return response


def get_fastapi_app(
    conn_url: str = "memory://localhost/",
    in_queue_name: str = "queue_in",
    in_exchange_name: str = "in_excahnge",
    in_routing_key: str = "api_model_input",
):
    app = FastAPI()
    producer_middleware = ProducerMiddleware(
        conn_url=conn_url,
        in_queue_name=in_queue_name,
        in_exchange_name=in_exchange_name,
        in_routing_key=in_routing_key,
    )
    app.add_middleware(producer_middleware)
    return app
