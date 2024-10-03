from config.config import settings
from config.logger_config import get_logger
from bs4 import BeautifulSoup
import aiohttp


logger = get_logger(__name__)


async def get_all_cars(count: str = 1):
    '''
    Парсинг страницы машин
    '''

    async with aiohttp.ClientSession() as session:
        async with session.get(f'{settings.BASE_URL}/{count}') as response:
            try:
                if response.status == 200:
                    logger.info('Получили страницу с машинами')
                    return await response.text()
            except Exception as e:
                logger.critical('Ошибка в получении страницы с машинами')

async def get_page_counts():
    '''
    Получение последней страницы
    '''

    async with aiohttp.ClientSession() as session:
        async with session.get(f'{settings.BASE_URL}/10000') as response:
            if response.status == 200:
                logger.info('Получили последнюю страницу')
                return await response.text()


async def parse_counts():
    '''
    Получение количества страниц
    '''
    try:
        html = await get_page_counts()

        soup = BeautifulSoup(html, 'lxml')

        count = soup.find_all('a', class_='page-link')[-1]

        logger.info('Получили количество страниц')
        return [1,count.get('data-page')]
    except Exception as e:
        logger.critical(f'Ошибка в получении количества страниц - {e}')