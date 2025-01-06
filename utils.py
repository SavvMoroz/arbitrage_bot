import asyncio
import ccxt.async_support as ccxt
import sys
from config import EXCHANGES
from config import CURRENCIES
import logging
from db import main_db

logging.basicConfig(level=logging.INFO)

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


# create list objects ccxt.Exchange
def generate_exchange_list(exchanges_names: list) -> list[ccxt.Exchange]:
    exchange_list = []
    for exchange in exchanges_names:
        exchange_list.append(getattr(ccxt, exchange)())
    return exchange_list


async def fetch_price(exchange: ccxt.Exchange, currency: str) -> dict:
    data = {
        "pair": currency,
        "exchange": exchange.name,
        "bids": None,
        "asks": None,
    }
    try:
        price = await exchange.fetch_order_book(f"{currency}")
        data["bids"] = price["bids"][0][0] if price["bids"] else None
        data["asks"] = price["asks"][0][0] if price["asks"] else None
    except ccxt.BadSymbol:  # if exchange das not have currency, we skip it
        pass
    except Exception as e:
        logging.error(f"{exchange.name} - {currency}: {e}")

    return data
    # finally:
    #     await exchange.close()


async def main():
    exchanges_objects = [getattr(ccxt, exchange)() for exchange in EXCHANGES]
    tasks = []

    for exchange in exchanges_objects:
        for currency in CURRENCIES:
            tasks.append(fetch_price(exchange, currency))

    data = await asyncio.gather(*tasks)

    await main_db(data)
    # print(data)

    for exchange in exchanges_objects:
        await exchange.close()


if __name__ == '__main__':
    while True:
        asyncio.run(main())
