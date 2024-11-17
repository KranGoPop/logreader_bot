import json
import os
from telegram import Bot
from telegram.constants import ParseMode
import logging

from .format_description import format_description
from src.message import get_log_message

logger = logging.getLogger(__name__)


def get_numeric_log_level(level_name: str) -> int:
    numeric_level = logging.getLevelName(level_name.upper())
    if isinstance(numeric_level, int):
        return numeric_level
    else:
        logger.error(f"Уровень логирования '{level_name}' не найден.")
        return 30
    

async def send_all(config: dict, offset: dict, id: str, msg: int, status: str, bot: Bot) -> None:
    text, markup = get_log_message(offset, id, msg, status)
    for client_tid in config['clients']:
        await bot.send_message(
            chat_id=client_tid,
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=markup,
        )


async def reader(offset: dict, config: dict, id: str, bot: Bot) -> None:
    try:
        with open(offset['id2path'][id], 'r') as f:
            seek = offset[id + '_seek']
            f.seek(0, os.SEEK_END)
            seek_end = f.tell()
            
            if seek > seek_end:
                offset[id + '_seek'] = 0
                seek = 0
            f.seek(seek)
            
            archive_rec = {}
            is_archive_rec_empty = True
            for line in f:
                sections = line.split(' -#@- ')
                
                if len(sections) != 4:
                    if is_archive_rec_empty:
                        continue
                    else:
                        archive_rec['desc'].append(line)
                else:
                    if not is_archive_rec_empty:
                        short_desc, desc = format_description(archive_rec['desc'])
                        archive_rec['short_desc'] = short_desc
                        archive_rec['desc'] = desc
                        
                        with open('./archive/' + id + '.jsonl', 'a') as af:
                            archive_rec_seek = af.tell()
                            af.write(json.dumps(archive_rec) + '\n')
                        
                        await send_all(config, offset, id, archive_rec_seek, 'close', bot)
                        is_archive_rec_empty = True
                    
                    
                    if get_numeric_log_level(sections[2]) >= 30:
                        archive_rec['time'] = sections[0]
                        archive_rec['module'] = sections[1]
                        archive_rec['level'] = sections[2]
                        archive_rec['desc'] = [sections[3]]
                        is_archive_rec_empty = False
                        
            if not is_archive_rec_empty:
                        short_desc, desc = format_description(archive_rec['desc'])
                        archive_rec['short_desc'] = short_desc
                        archive_rec['desc'] = desc
                        
                        with open('./archive/' + id + '.jsonl', 'a') as af:
                            archive_rec_seek = af.tell()
                            af.write(json.dumps(archive_rec) + '\n')
                        
                        await send_all(config, offset, id, archive_rec_seek, 'close', bot)

            
            new_seek = f.tell()
            offset[id + '_seek'] = new_seek
            with open('./archive/offset.json', 'w') as f:
                json.dump(offset, f, indent=2)
    except FileNotFoundError:
        logger.error(f"file {offset['id2path'][id]} not found")
                
        
        
        