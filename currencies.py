import ccxt
import ccxt.pro as ccxtpro
import asyncio
import sys
from config import EXCHANGES
from config import CURRENCIES
from db import main_db
import logging

logging.basicConfig(level=logging.INFO)

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def watch_price(exchange: ccxtpro.Exchange, currency: str):
    data = {
        "pair": currency,
        "exchange": exchange.name,
        "bids": None,
        "asks": None,
    }

    try:
        logging.info(f"Fetching price for {exchange.name} - {currency}")
        price = await exchange.watch_order_book(f"{currency}")
        data["bids"] = price["bids"][0][0] if price["bids"] else None
        data["asks"] = price["asks"][0][0] if price["asks"] else None
        logging.info(f"Price fetched for {exchange.name} - {currency}: {data}")
        # await main_db(data=data)
        # await asyncio.sleep(0.2)
    except ccxt.BadSymbol:
        pass
    except ccxt.NetworkError as e:
        logging.error(f"{exchange.name} - {currency} - NetworkError - {e}")
        await asyncio.sleep(0.5)
    except Exception as e:
        logging.error(f"{exchange.name} - {currency} - {e}")
        # await main_db(data=data)

    return data


async def main():
    # exchanges_objects = [getattr(ccxtpro, exchange)() for exchange in EXCHANGES]
    tasks = []
    logging.info("Starting tasks for exchanges and currencies...")
    for exchange_name in EXCHANGES:
        for currency in CURRENCIES:
            exchange = getattr(ccxtpro, exchange_name)()
            tasks.append(asyncio.create_task(watch_price(exchange, currency)))

    result = await asyncio.gather(*tasks, return_exceptions=True)

    # for exchange in exchanges_objects:
    #     for currency in CURRENCIES:
    #         tasks.append(watch_price(exchange, currency))

    # await asyncio.gather(*tasks)
    # await main_db(data)
    # await main_db(data)
    # print(data)

    # for task in tasks:
    #     exchange = task.get_coro().cr_frame.f_locals.get("exchange")
    #     if exchange:
    #         await exchange.close()
    # for exchange in exchanges_objects:
    #     await exchange.close()

    # await watch_price()
    # await exchange.close()


async def runner():
    while True:
        await main()


if __name__ == '__main__':
    asyncio.run(runner())
