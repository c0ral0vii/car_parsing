from config.config import settings
import csv
import aiofiles
import datetime
from config.logger_config import setup_async_logger
import asyncio

logger = asyncio.run(setup_async_logger())


async def create():
    '''
    Создание csv-файла
    '''

    base_info = ['title',
        'guid',
        'URL',
        'price',
        'images_link',
        'configurate',
        'engine',
        'transmission',
        'probeg',
        'issue',
        'taxt'] # структура файла

    async with aiofiles.open(f'./output/parse.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        await writer.writerow(base_info)
    
    logger.info('Файл parse.csv создан')

        