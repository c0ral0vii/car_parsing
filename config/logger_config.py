from loguru import logger


async def setup_async_logger():
    '''
    Логер
    '''

    logger.remove()

    logger.add('debug.log', level='INFO', colorize=True, rotation='100 MB', compression='zip', format='{time} | {level} | {message}', mode='w')

    return logger