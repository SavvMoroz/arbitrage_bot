import ccxt as ccxt
import asyncio
import sys


kraken = ccxt.kraken()


# print(kraken.fetch_order_book("BNB/USDT"))

try:
    price = kraken.fetch_order_book("BNB/USDT")
except ccxt.BadSymbol as e:
    print(e)




# print(type(prices))









# def square(x):
#     return x ** 3
#
#
# if __name__ == '__main__':
#     t = time.time()
#     n = [1433455343456363423, 12465634321, 14576467457467234, 465564645654764764, 34553563543]
#     with Pool(processes=3) as pool:
#         results = pool.map(square, n)
#         print(results)
#         print(time.time() - t)
