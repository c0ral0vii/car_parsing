import asyncio
from func.create import create
from parser.parser import main




async def start():
    await create()
    
    await main()
    

if __name__ == '__main__':
    print('Старт')
    asyncio.run(start())
    print('Закончил')