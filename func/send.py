import ftplib
from config.logger_config import setup_async_logger
import asyncio

logger = asyncio.run(setup_async_logger())


def send():
    '''
    Отправка на сервер
    '''

    logger.info('Отправка файла на сервер')
    ftp = ftplib.FTP("46.254.17.27")
    ftp.login("ftp_pars", "n8N5ipG26J")
    localfile = f'./output/parse.csv'
    remotefile = 'pars_by.csv'
    with open(localfile, "rb") as file:
        ftp.storbinary('STOR ' + remotefile, file)

    ftp.quit()
    logger.info('Отправка завершена')
