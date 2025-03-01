import logging
import asyncpg
import asyncio
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


async def create():
    conn = await asyncpg.connect(
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME'),
        host=os.getenv('DB_HOST'),
    )
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS prices(
        id SERIAL PRIMARY KEY,
        pair TEXT NOT NULL,
        exchange VARCHAR NOT NULL,
        bid numeric(18, 8),
        ask numeric(18, 8),
        update timestamp DEFAULT CURRENT_TIMESTAMP,
        CONSTRAINT uix_pair_exchange UNIQUE (pair, exchange)
        )
        ''')


async def connect_to_db():
    return await asyncpg.connect(
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME'),
        host=os.getenv('DB_HOST'),
    )


async def create_pool():
    return await asyncpg.create_pool(
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME'),
        host=os.getenv('DB_HOST'),
    )


async def upsert_data(pool, data):
    query = """
    INSERT INTO prices (pair, exchange, bid, ask)
    VALUES ($1, $2, $3, $4)
    ON CONFLICT (pair, exchange) DO UPDATE SET
    bid = EXCLUDED.bid,
    ask = EXCLUDED.ask,
    update = CURRENT_TIMESTAMP
    """

    async with pool.acquire() as connection:
        await connection.execute(
            query,
            data["pair"],
            data["exchange"],
            data["bids"],
            data["asks"],
        )


async def find_arbitrage_opportunities(pool, queue, min_percent: float, max_percent: float):
    async with pool.acquire() as connection:
        async with connection.transaction():
            query = """
            WITH Arbitrage AS (
            SELECT p1.pair,
                   p1.exchange AS buy_exchange,
                   p1.ask AS buy_price,
                   p2.exchange AS sell_exchange,
                   p2.bid AS sell_price,
                   p2.bid - p1.ask AS profit,
                   ((p2.bid - p1.ask) / p1.ask) * 100 AS profit_percent
            FROM prices p1
            JOIN prices p2 ON p1.pair = p2.pair AND p1.exchange <> p2.exchange
            WHERE p2.bid > p1.ask
            )
            SELECT *
            FROM Arbitrage
            WHERE profit_percent BETWEEN $1 AND $2
            ORDER BY profit_percent DESC;
            """

            rows = await connection.fetch(query, min_percent, max_percent)

            # print(rows)

            for row in rows:
                opportunity = {
                    "pair": row["pair"],
                    "exchange_ask": row["buy_exchange"],
                    "ask": row["buy_price"],
                    "exchange_bid": row["sell_exchange"],
                    "bid": row["sell_price"],
                    "spread_percent": (row["sell_price"] - row["buy_price"]) / row["buy_price"] * 100
                }

                await queue.put(opportunity)
                # print(opportunity)
                # logging.info(f"arbitrage: {opportunity}")


async def main_db(data):
    pool = await asyncpg.create_pool(
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME'),
        host=os.getenv('DB_HOST'),
    )

    await upsert_data(pool, data)
    await pool.close()
