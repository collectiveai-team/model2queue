import time

from model2queue import api_task_producer, start_api_task_consumer


def test_base_api_task_consumer():
    global result
    result = None

    def predict_input(input):
        global result
        result = input

    worker = start_api_task_consumer(predict_input)

    @api_task_producer()
    def produce(input: str) -> str:
        return f"input => {input}"

    produce("hello")
    while result is None:
        time.sleep(0.1)

    assert result == "input => hello"
    worker.stop_consumer()


def test_change_queue_api_task_consumer():
    global result
    result = None
    in_queue_name = "test_in_queue"

    def predict_input(input):
        global result
        result = input

    worker = start_api_task_consumer(predict_input, in_queue_name=in_queue_name)

    @api_task_producer(in_queue_name=in_queue_name)
    def produce(input: str) -> str:
        return f"input => {input}"

    produce("hello")
    while result is None:
        time.sleep(0.1)

    assert result == "input => hello"
    worker.stop_consumer()
