from config.config import settings
from config.logger_config import get_logger
from bs4 import BeautifulSoup
import aiohttp
import asyncio


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
            try:
                if response.status == 200:
                    logger.info('Получили страницу с машинами')
                    return await response.text()
            except Exception as e:
                logger.critical('Ошибка в получении страницы с машинами')


async def parse_counts() -> list:
    '''
    Получение количества страниц
    '''

    try:
        html = await get_page_counts()

        soup = BeautifulSoup(html, 'lxml')

        count = soup.find_all('a', class_='page-link')[-1].get('data-page')

        logger.info('Получили количество страниц')

        count_pages = []
        for i in range(1, int(count)):
            count_pages.append(i)

        logger.info(f'Получено {count} страниц')
        
        return count_pages

    except Exception as e:
        logger.critical(f'Ошибка в получении количества страниц - {e}')


async def parse_link_cars(counts: list):
    '''
    Получаем ссылки на машины
    '''

    logger.info('Получаем все ссылки на машины')
    
    
    for i in counts:
        all_links = []
        html = await get_all_cars(count=i)

        soup = BeautifulSoup(html, 'lxml')
        
        logger.info('Поиск ссылок на машины')
        links = soup.find_all('a', class_='btn btn-outline-primary')
        logger.info(f'Найдено {len(links)}')

        all_links.append(links)

        yield all_links # TODO


async def parse_page(link: str):
    '''
    Получение страницы с машиной
    '''

    async with aiohttp.ClientSession() as session:
        async with session.get(f'{link}') as response:
            try:
                if response.status == 200:
                    logger.info('Получили страницу с машинами')
                    html = await response.text()
            except Exception as e:
                logger.critical('Ошибка в получении страницы с машинами')

    soup = BeautifulSoup(html, 'lxml')

    configurate = {} # собираем  в одну конфигурацию машины

    name = soup.find('h1', class_='mb-5 mt-4').get('text')
    logger.info(f'Собираем машину {link} - {name}')
    configurate_car = soup.find('div', class_='row row-cols-1 row-cols-md-2 g-1')


async def main():
    '''
    Основная функция
    '''

    count_pages = await parse_counts()
    logger.info('Получили колличество страниц')

    async for all_links in parse_link_cars(counts=count_pages):
        print('Начало:',all_links)