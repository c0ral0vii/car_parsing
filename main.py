import asyncio
from config.logger_config import setup_async_logger
from func.create import create
from parser.parser import main
from func.send import send


logger = asyncio.run(setup_async_logger())


async def start():
    logger.info('Запуск программы')
    await create()
    tasks = [main() for _ in range(1)]
    await asyncio.gather(*tasks)
    logger.info('Создали файл')
    logger.info('Парсинг закончился')
    logger.info('Отправка файла')
    send()
    logger.info('Отправлено')



if __name__ == '__main__':
    logger.info('Старт')
    asyncio.run(start())
    logger.info('Закончил')