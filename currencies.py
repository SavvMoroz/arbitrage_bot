import ccxt.pro as ccxtpro
import ccxt.async_support as ccxt
import asyncio
import sys
# import time
from config import EXCHANGES
from config import CURRENCIES

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
