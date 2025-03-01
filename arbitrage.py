import asyncio
from db import find_arbitrage_opportunities
from db import create_pool
import sys

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def process_arbitrage_opportunities():
    queue = asyncio.Queue()
    pool = await create_pool()

    min_percent = 1
    max_percent = 5

    while True:
        await find_arbitrage_opportunities(pool, queue, min_percent, max_percent)
        while not queue.empty():
            opportunity = await queue.get()
            print("arbitrage:", opportunity)
        await asyncio.sleep(0.5)
