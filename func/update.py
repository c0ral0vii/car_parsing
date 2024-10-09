import csv
import aiofiles


async def update_csv(data: list):
    '''
    Дополнение csv-файла
    '''

    async with aiofiles.open('./output/parse.csv', 'a', encoding='utf-8') as file: 
        writer = csv.writer(file)
        await writer.writerow(data)
