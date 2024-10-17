import asyncio
import aiohttp
import numpy as np
import csv
import aiofiles
import ftplib
import os
from loguru import logger
from pydantic_settings import BaseSettings, SettingsConfigDict
from bs4 import BeautifulSoup


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    BASE_URL: str = 'https://carskorea.shop'


settings = Config()


async def setup_async_logger():
    '''
    Логер
    '''

    logger.remove()

    logger.add('debug.log', level='INFO', colorize=True, rotation='100 MB', compression='zip', format='{time} | {level} | {message}', mode='w')

    return logger


logger = asyncio.run(setup_async_logger())


async def send():
    '''
    Отправка на сервер
    '''
    try:
        logger.info('Отправка файла на сервер')
        ftp = ftplib.FTP("46.254.17.27")
        ftp.login("ftp_pars", "n8N5ipG26J")
        localfile = f'./output/parse.csv'
        remotefile = 'pars_by.csv'
        with open(localfile, "rb") as file:
            ftp.storbinary('STOR ' + remotefile, file)

        ftp.quit()
        logger.info('Отправка завершена')
    except Exception as e:
        logger.error(f'Ошибка при отправке {e}')


async def update_csv(data: list):
    '''
    Дополнение csv-файла
    '''
    
    try:
        if len(data) != 11:
            return

        async with aiofiles.open('./output/parse.csv', 'a', encoding='utf-8', newline='') as file: 
            writer = csv.writer(file)
            await writer.writerow(data)
    except Exception as e:
        logger.critical(f'Ошибка при записи файла, {e}')


async def create():
    '''
    Создание csv-файла
    '''

    base_info = [
        'title',
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
        logger.info('Получаем колличество страниц')
        html = await get_page_counts(session=session)

        soup = BeautifulSoup(html, 'lxml')

        count = soup.find_all('a', class_='page-link')[-1].get('data-page')


        count_pages = []
        for i in range(1, int(count)):
            count_pages.append(i)

        logger.info(f'Получено страниц - {len(count_pages)}')
        return count_pages

    except Exception as e:
        logger.critical(f'Невозможно получить количество страниц \n {e}')
        print(e)


async def parse_link_cars(session, pages: list = []) -> list:
    '''
    Получаем ссылки на машины
    '''

    if len(pages) == 0:
        logger.critical('Ошибка с получением страниц')
        raise 'Ошибка с получением страниц перезапустите скрипт'

    all_links = []

    for i in pages:
        try:

            html = await get_all_cars(session=session, count=i)
            if not html:
                continue
            soup = BeautifulSoup(html, 'lxml')
            
            links = soup.find_all('a', class_='btn btn-outline-primary')
            for link in links:
                all_links.append(f'{settings.BASE_URL}{link.get('href')}')
                logger.info(f'Ссылка получена {settings.BASE_URL}{link.get('href')}')
        except Exception as e:
            logger.error(f'Возникла ошибка {e} при получении ссылок на машины')
            continue

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

    try:
        name = soup.find('h1', class_='mb-5 mt-4').get_text()
        id = soup.find('div', class_='text-secondary h5 negative-mt-4').get_text(strip=True)
        price_element = soup.find('span', itemprop='price')

        if price_element:
            price_ = price_element.get_text(strip=True).encode('utf-8').decode('utf-8')
            price = int(price_.replace('\xa0', '').replace(' ', ''))
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
                price,
                ' | '.join([image_link.get('src').replace('?impolicy=heightRate&rh=653&cw=1160&ch=653&cg=Center', '') for image_link in image_links]),
                ready_config[0],
                ready_config[1],
                ready_config[2],
                ready_config[4],
                ready_config[5][-4:],
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
    async with aiohttp.ClientSession() as session: 
        logger.info('Получили колличество страниц')

        for link in pages:
            data = await parse_page(link=link, session=session)
            await update_csv(data=data)


async def start(processes: int = 1):
    print('Смотрите файл логов debug.log')

    logger.info('Запуск программы')
    logger.info(f'Запуск в {processes} процессов')

    try:
        os.mkdir('./output')
        logger.info('Папка output создана')
    except Exception as e:
        logger.error('Папка уже существует')

    await create()
    async with aiohttp.ClientSession() as session:
        all_pages = await parse_counts(session=session)
        links_part = np.array_split(all_pages, processes)
        get_tasks = [parse_link_cars(session=session, pages=page_row) for page_row in links_part]
        logger.info('Получаем ссылки на машины')
        all_cars = await asyncio.gather(*get_tasks)

    tasks = [main(pages=links) for links in all_cars]
    await asyncio.gather(*tasks)
    logger.info('Создали файл')

    logger.info('Парсинг закончился')

    logger.info('Отправка файла')
    await send()
    logger.info('Отправлено')



if __name__ == '__main__':
    logger.info('Старт')
    asyncio.run(start(processes=100))
    logger.info('Закончил')