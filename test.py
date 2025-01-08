import ccxt
import ccxt.pro as ccxtpro
import asyncio
import sys
import logging
from config import EXCHANGES, CURRENCIES
from db import main_db, upsert_data, create_pool, create

logging.basicConfig(level=logging.INFO)

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


# this function receive data from function "fetch_and_send_to_queue_price" in queue, them send to DB
async def db_worker(queue: asyncio.Queue, pool):
    while True:
        data = await queue.get()
        try:
            await upsert_data(pool, data)
        except Exception as e:
            logging.error(e)
        finally:
            queue.task_done()


async def fetch_and_send_to_queue_price(currency: str, exchange: str, queue) -> None:
    async with getattr(ccxtpro, exchange)() as exchange:
        try:
            while True:
                price = await exchange.watch_order_book(f"{currency}")

                data = {"pair": currency, "exchange": exchange.name,
                        "bids": price["bids"][0][0] if price["bids"] else None,
                        "asks": price["asks"][0][0] if price["asks"] else None}

                # print(data)

                await queue.put(data)
                # await asyncio.sleep(0.2)

        except ccxt.BadSymbol:
            pass
        except Exception as e:
            logging.error(e)


async def main():
    pool = await create_pool()  # create DB connection pool
    queue = asyncio.Queue()

    db_task = asyncio.create_task(db_worker(queue, pool))

    tasks = []
    for currency in CURRENCIES:
        for exchange in EXCHANGES:
            tasks.append(asyncio.create_task(fetch_and_send_to_queue_price(currency, exchange, queue)))

    await asyncio.gather(*tasks)

    await queue.join()
    await pool.close()
    db_task.cancel()


if __name__ == '__main__':
    # asyncio.run(create())
    asyncio.run(main())
