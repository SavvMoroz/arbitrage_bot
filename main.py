import ccxt.pro as ccxtpro
import ccxt
import asyncio
import time
import sys

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
