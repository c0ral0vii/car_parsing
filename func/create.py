from openpyxl import Workbook
from config.config import settings


async def create():
    '''
    Создание excel файла
    '''

    wb = Workbook()
    ws = wb.active
    ws.title = "Cars"
    ws.append(
        ['title',
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
        'taxt']
        )
    wb.save(f'output/{settings.BASE_NAME}')
    return wb

        