from threading import Thread

from model2queue.helper.logger import get_logger

logger = get_logger(__name__)


class WorkerThread(Thread):
    def __init__(self, worker, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.worker = worker

    def stop_consumer(self):
        self.worker.should_stop = True
        logger.info("stopped consumer")
