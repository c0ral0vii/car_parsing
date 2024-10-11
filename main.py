import asyncio
import aiohttp
import numpy as np
from config.logger_config import setup_async_logger
from func.create import create
from parser.parser import main, parse_link_cars
from func.send import send


logger = asyncio.run(setup_async_logger())


async def start(processes: int = 1):
    logger.info('Запуск программы')
    await create()
    async with aiohttp.ClientSession() as session:
        all_links = await parse_link_cars(session=session)

        links_part = np.array_split(all_links, processes)

    print('Смотрите файл логов debug.log')

    tasks = [main(pages=links) for links in links_part]
    await asyncio.gather(*tasks)
    logger.info('Создали файл')

    logger.info('Парсинг закончился')

    logger.info('Отправка файла')
    send()
    logger.info('Отправлено')



if __name__ == '__main__':
    logger.info('Старт')
    asyncio.run(start(processes=50))
    logger.info('Закончил')