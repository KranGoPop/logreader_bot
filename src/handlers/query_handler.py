from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from typing import cast
from src.message import get_log_message
import base64


async def query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.callback_query:
        config: dict = context.bot_data['config']
        offset: dict = context.bot_data['offset']
        cb_query = update.callback_query
        await cb_query.answer()
        
        cb_data = cast(str, cb_query.data).split('?')
        status = 'full' if cb_data[0][0] == 'f' else 'close'
        msg = int(base64.b64decode(cb_data[1]))
        id = offset['num2id'][cb_data[0][1:]]
        
        text, markup = get_log_message(offset, id, msg, status)
        
        await cb_query.edit_message_text(text=text, reply_markup=markup, parse_mode=ParseMode.HTML)