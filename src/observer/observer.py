from watchdog.events import DirModifiedEvent, FileModifiedEvent, FileSystemEventHandler
from queue import Queue
import logging
import os


logger = logging.getLogger(__name__)


class LogHandler(FileSystemEventHandler):
    def __init__(self, file_name: str, id: str, queue: Queue):
        super().__init__()
        self.file_name = file_name
        self.queue = queue
        self.id = id
        
    
    def on_modified(self, event: DirModifiedEvent | FileModifiedEvent) -> None:
        logger.info(f"File modified src_path={event.src_path} and fp={self.file_name}")
        if event.src_path.replace(os.sep, '/') == self.file_name:
            self.queue.put(self.id)
            logger.info(f"File modified {self.file_name}")