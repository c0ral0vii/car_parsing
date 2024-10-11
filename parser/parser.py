from config.config import settings
from bs4 import BeautifulSoup
from func.update import update_csv
import aiohttp
import asyncio
from config.logger_config import setup_async_logger
import asyncio

logger = asyncio.run(setup_async_logger())


async def get_all_cars(session, count: str = 1):
    '''
    Парсинг страницы машин
    '''

    async with session.get(f'{settings.BASE_URL}/{count}') as response:
        try:
            if response.status == 200:
                return await response.text()
            else:
                logger.error('Ошибка при получении машин')
                return
        except Exception as e:
            logger.exception(f'Ошибка {e} при парсинге страницы с машинами')


async def get_page_counts(session):
    '''
    Получение последней страницы
    '''

    async with session.get(f'{settings.BASE_URL}/10000') as response:
        try:
            if response.status == 200:
                return await response.text()
            else:
                logger.error('Ошибка при получении машин')
                return
        except Exception as e:
            logger.exception(f'Ошибка {e} при парсинге страницы с машинами')


async def parse_counts(session) -> list:
    '''
    Получение количества страниц
    '''

    try:
        html = await get_page_counts(session=session)

        soup = BeautifulSoup(html, 'lxml')

        count = soup.find_all('a', class_='page-link')[-1].get('data-page')


        count_pages = []
        for i in range(1, int(count)):
            count_pages.append(i)

        return count_pages

    except Exception as e:
        print(e)


async def parse_link_cars(session):
    '''
    Получаем ссылки на машины
    '''

    logger.info('Получаем ссылки на машины')
    all_links = []
    all_pages = await parse_counts(session=session)

    for i in all_pages:
        try:
            html = await get_all_cars(session=session, count=i)

            soup = BeautifulSoup(html, 'lxml')
            
            links = soup.find_all('a', class_='btn btn-outline-primary')
            for link in links:
                all_links.append(f'{settings.BASE_URL}/{link.get('href')}')
                logger.info(f'Ссылка получена {settings.BASE_URL}{link.get('href')}')
        except Exception as e:
            logger.error(f'Возникла ошибка {e} при получении ссылок на машины')
            continue
    logger.info(f'Получено ссылок на машины - {len(all_links)}')
    return all_links


async def parse_page(link: str, session):
    '''
    Получение страницы с машиной
    '''

    logger.info(f'Обрабатываем машину: {link}')

    try:
        async with session.get(f'{link}') as response:
            if response.status == 200:
                html = await response.text()
            else:
                logger.debug(f'{link} - {response.status}')
                return

        soup = BeautifulSoup(html, 'lxml')
    except Exception as e:
        logger.exception(f'Ошибка с машиной: {link}, проблема получения html страницы')
        return

    # configurate = {} # собираем  в одну конфигурацию машины
    try:
        name = soup.find('h1', class_='mb-5 mt-4').get_text()
        id = soup.find('div', class_='text-secondary h5 negative-mt-4').get_text()
        price_element = soup.find('span', itemprop='price')

        if price_element:
            price = price_element.get_text(strip=True)
        else:
            price = 'Отсутствует, только связь с менеджером'

        configurate_car = soup.find('div', class_='row row-cols-1 row-cols-md-2 g-1')
        image_links = soup.find_all('img', class_='w-100 rounded img-fluid swiper-car-view')

        brand_select = soup.find('select', id='analyticsearch-brand_id')
        brand_option = brand_select.find('option', selected=True).get_text(strip=True)

        ready_config = []

        for item in configurate_car.find_all('td'):
            if not item.get('class'):
                ready_config.append(item.get_text())
        
        data = [
                name, 
                id.split(' ')[-1],
                link,
                price.encode('utf-8'),
                ','.join([image_link.get('src').replace('impolicy=heightRate&rh=653&cw=1160&ch=653&cg=Center', '') for image_link in image_links]),
                ready_config[0],
                ready_config[1],
                ready_config[2],
                ready_config[4],
                ready_config[5],
                f'{brand_option}>{' '.join(name.split(',')[0].split(' ')[1:])}>{ready_config[0]}'
                ]

        logger.info(f'Машина обработана: {link}')
        return data
    except Exception as e:
        logger.exception(f'Ошибка с машиной: {link}, {e}')
        return
    

async def main(pages: list):
    '''
    Основная функция
    '''

    logger.info('Запуск основной функции')
    async with aiohttp.ClientSession() as session: # TODO получить количество в main функции
        logger.info('Получили колличество страниц')

        for link in pages:
            data = await parse_page(link=link, session=session)
            await update_csv(data=data)