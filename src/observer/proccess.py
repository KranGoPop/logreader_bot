from watchdog.observers import Observer
from .observer import LogHandler
import os
from queue import Queue
import logging


logger = logging.getLogger(__name__)


def init_observer(offset: dict, queue: Queue) -> any:
    observer = Observer()
    for key, val in offset['id2path'].items():
        directory = os.path.dirname(val)
        event_handler = LogHandler(val, key, queue)
        observer.schedule(event_handler, directory, recursive=False)
    
    logger.info("Observer initialized")
    observer.start()
    return observer


def stop_observer(observer) -> None:
    observer.stop()
    observer.join()
    logger.info("Observer stopped")