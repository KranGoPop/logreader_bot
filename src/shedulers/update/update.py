from telegram import Bot
from queue import Queue
import logging
import asyncio
from src.logreader import reader


logger = logging.getLogger(__name__)


async def stop_update_capture(task_data: dict) -> None:
    task_data['end'] = True
    await task_data['event'].wait()


async def update_capture(task_data: dict, bot: Bot) -> None:
    queue: Queue = task_data['queue']
    offset: dict = task_data['offset']
    config: dict = task_data['config']

    logger.info("Update Capture job started")

    while not task_data['end']:
        while queue.empty() and not task_data['end']:
            await asyncio.sleep(5)
        update = {}
        counter = 0
        while not queue.empty() and counter < 10:
            update_id = queue.get(False)
            update[update_id] = True
            counter += 1

        await asyncio.sleep(5)

        for id in update.keys():
            await reader(offset, config, id, bot)

    logger.info("Update Capture job stopped")
    task_data['event'].set()
