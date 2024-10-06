import asyncio
from config.logger_config import get_logger
from parser import parser


logger = get_logger(__name__)


async def start():
    await parser.main()


asyncio.run(start())