from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
import base64
import json


def get_log_message(offset: dict, id: str, msg: int, status: str) -> list[str, InlineKeyboardMarkup]:
    with open('./archive/' + id + '.jsonl', 'r') as f:
        f.seek(msg)
        record = json.loads(f.readline())
    
    if record['level'] == "ERROR":
        level_emodji = '❗'
    elif record['level'] == "WARNING":
        level_emodji = '⚠️'
    else:
        level_emodji = '👿'
    
    text = f"""
{level_emodji} - {id}
<b>Time:</b> {record['time']}
<b>Module:</b> {record['module']}
<b>Desc:</b> {record['desc'] if status == 'full' else record['short_desc']}
    """
    
    query_id = str(offset['id2num'][id]) + '?' + base64.b64encode(str(msg).encode()).decode()
    if status == 'full':
        markup = InlineKeyboardMarkup([[
            InlineKeyboardButton(
                '☝️ Сжать',
                callback_data='c' + query_id
            )
        ]])
    else:
        markup = InlineKeyboardMarkup([[
            InlineKeyboardButton(
                '👇 Показать',
                callback_data='f' + query_id
            )
        ]])
    
    if record['short_desc'] == record['desc']:
        markup = None
    
    return text, markup
    