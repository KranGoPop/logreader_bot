import logging
from logging.handlers import RotatingFileHandler
import json
import sys
import asyncio
from queue import Queue
from src.handlers import query_handler
from src.logreader import reader_init
from src.observer import stop_observer, init_observer
from src.shedulers.update import update_capture, stop_update_capture

from telegram.ext import Application, CallbackQueryHandler


logging.basicConfig(
    format="%(asctime)s -#@- %(name)s -#@- %(levelname)s -#@- %(message)s", 
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout),
        RotatingFileHandler(
            "log/bot.log",
            maxBytes=5 * 1024 * 1024,
            backupCount=10
        ),
    ]
)
logging.getLogger("httpx").setLevel(logging.WARNING)


def main() -> None:
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("Config file does not exist.")
        sys.exit(1)

    application = Application.builder().token(config["telegram"]["token"]).build()
    application.bot_data = {
        'config': config,
        'bot': application.bot,
    }
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    loop.run_until_complete(reader_init(config, application))
    try:
        with open('./archive/offset.json', 'r') as f:
            offset = json.load(f)
    except FileNotFoundError:
        print("Offset file does not exist.")
        sys.exit(1)
    
    update_queue = Queue()
    
    update_task_data = {
        'event': asyncio.Event(),
        'end': False,
        'config': config,
        'offset': offset,
        'queue': update_queue,
    }
    loop.create_task(update_capture(update_task_data, application.bot))
    observer = init_observer(offset, update_queue)
    
    application.add_handler(CallbackQueryHandler(query_handler))
    
    application.run_polling(close_loop=False)
    
    loop.run_until_complete(stop_update_capture(update_task_data))
    stop_observer(observer)


if __name__ == "__main__":
    main()