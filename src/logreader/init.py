import json
from telegram.ext import Application
import os

from .reader import reader


async def reader_init(config: dict, application: Application) -> dict:
    try:
        with open('./archive/offset.json', 'r') as f:
            offset = json.load(f)
    except FileNotFoundError:
        offset = {}
        offset['num2id'] = {}
        offset['id2num'] = {}
        offset['id2path'] = {}
        for i, log_rec in enumerate(config['logs']):
            offset['id2num'][log_rec['id']] = str(i)
            offset['num2id'][str(i)] = log_rec['id']
            offset['id2path'][log_rec['id']] = log_rec['log_path'].replace(os.sep, '/')
            offset[str(log_rec['id']) + '_seek'] = 0
    
    max_num = int(max(offset['num2id'].keys())) + 1
    for log_rec in config['logs']:
        if offset['id2num'].get(log_rec['id'], -1) == -1:
            offset['id2num'][log_rec['id']] = str(max_num)
            offset['num2id'][str(max_num)] = log_rec['id']
            offset['id2path'][log_rec['id']] = log_rec['log_path'].replace(os.sep, '/')
            offset[str(log_rec['id']) + '_seek'] = 0
            max_num += 1
    
    with open('./archive/offset.json', 'w') as f:
        json.dump(offset, f, indent=2)
    
    application.bot_data['offset'] = offset
         
    for id in offset['id2path'].keys():
        await reader(offset, config, id, application.bot)
    
    