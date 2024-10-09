from config.config import settings
import csv
import aiofiles
import datetime


async def create():
    '''
    Создание csv-файла
    '''
    data = datetime.datetime.now().strftime('%Y-%m-%d')
    base_info = ['title',
        'guid',
        'URL',
        'price',
        'images_link',
        'configurate',
        'date',
        'engine',
        'transmission',
        'probeg',
        'issue',
        'taxt'] # структура файла

    async with aiofiles.open(f'./output/parse.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        await writer.writerow(base_info)
        