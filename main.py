import asyncio
import sys
from test import main as main_test
from arbitrage import process_arbitrage_opportunities

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def main():
    task1 = asyncio.create_task(main_test())
    task2 = asyncio.create_task(process_arbitrage_opportunities())

    await asyncio.gather(task1, task2)

if __name__ == '__main__':
    asyncio.run(main())
