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


async def main_db(data):
    pool = await asyncpg.create_pool(
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME'),
        host=os.getenv('DB_HOST'),
    )

    await upsert_data(pool, data)
    await pool.close()
