from config.config import settings
from bs4 import BeautifulSoup
from func.update import update_excel
import aiohttp
import asyncio



async def get_all_cars(count: str = 1):
    '''
    Парсинг страницы машин
    '''

    async with aiohttp.ClientSession() as session:
        async with session.get(f'{settings.BASE_URL}/{count}') as response:
            try:
                if response.status == 200:
                    return await response.text()
            except Exception as e:
                print(e)


async def get_page_counts():
    '''
    Получение последней страницы
    '''

    async with aiohttp.ClientSession() as session:
        async with session.get(f'{settings.BASE_URL}/10000') as response:
            try:
                if response.status == 200:
                    return await response.text()
            except Exception as e:
                print(e)


async def parse_counts() -> list:
    '''
    Получение количества страниц
    '''

    try:
        html = await get_page_counts()

        soup = BeautifulSoup(html, 'lxml')

        count = soup.find_all('a', class_='page-link')[-1].get('data-page')


        count_pages = []
        for i in range(1, int(count)):
            count_pages.append(i)

        return count_pages

    except Exception as e:
        print(e)


async def parse_link_cars(counts: list):
    '''
    Получаем ссылки на машины
    '''

    print('Получаем все ссылки на машины')    
    
    for i in counts:
        all_links = []
        html = await get_all_cars(count=i)

        soup = BeautifulSoup(html, 'lxml')
        
        links = soup.find_all('a', class_='btn btn-outline-primary')

        for link in links:
            all_links.append(f'{settings.BASE_URL}/{link.get('href')}')

        yield all_links


async def parse_page(link: str):
    '''
    Получение страницы с машиной
    '''

    async with aiohttp.ClientSession() as session:
        async with session.get(f'{link}') as response:
            try:
                if response.status == 200:
                    html = await response.text()
            except Exception as e:
                print(e)

    soup = BeautifulSoup(html, 'lxml')

    configurate = {} # собираем  в одну конфигурацию машины

    name = soup.find('h1', class_='mb-5 mt-4').get_text()
    id = soup.find('div', class_='text-secondary h5 negative-mt-4').get_text()
    price = soup.find('span', itemprop='price').get_text(strip=True)

    configurate_car = soup.find('div', class_='row row-cols-1 row-cols-md-2 g-1')
    image_links = soup.find_all('img', class_='w-100 rounded img-fluid swiper-car-view')

    brand_select = soup.find('select', id='analyticsearch-brand_id')
    brand_option = brand_select.find('option', selected=True).get_text(strip=True)

    ready_config = []

    for item in configurate_car.find_all('td'):
        if not item.get('class'):
            ready_config.append(item.get_text())
    
    configurate.update({
        # 'title': name,
        # 'guid': id.split(' ')[-1],
        # 'URL': link,
        # 'price': price.encode('utf-8'),
        # 'images_link': [image_link.get('src') for image_link in image_links],
        # 'configurate': ready_config[0],
        # 'date': ready_config[3],
        # 'engine': ready_config[1],
        # 'transmission': ready_config[2],
        # 'probeg': ready_config[4],
        # 'issue': ready_config[5],
        # 'taxt': f'{brand_option}>{' '.join(name.split(',')[0].split(' ')[1:])}>{ready_config[0]}',
        'excel_format': [
            name, 
            id.split(' ')[-1],
            link,
            price.encode('utf-8'),
            [image_link.get('src') for image_link in image_links][0],
            ready_config[0],
            ready_config[3],
            ready_config[1],
            ready_config[2],
            ready_config[4],
            ready_config[5],
            f'{brand_option}>{' '.join(name.split(',')[0].split(' ')[1:])}>{ready_config[0]}'
            ]
    })
    asyncio.create_task(update_excel(data=configurate.get('excel_format')))


async def main():
    '''
    Основная функция
    '''

    count_pages = await parse_counts()

    async for all_links in parse_link_cars(counts=count_pages):
        for link in all_links:
            asyncio.create_task(parse_page(link=link))