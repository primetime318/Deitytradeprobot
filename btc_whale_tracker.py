# btc_whale_tracker.py

import asyncio
import logging
import aiohttp
import time

BTC_WHALE_THRESHOLD = 100_000  # USD threshold
BTC_PRICE_API = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
MEMPOOL_API = "https://mempool.space/api/mempool/recent"
SEEN_TX = set()
bot = None
GROUP_ID = None

async def fetch_btc_price():
    async with aiohttp.ClientSession() as session:
        async with session.get(BTC_PRICE_API) as resp:
            data = await resp.json()
            return data["bitcoin"]["usd"]

async def fetch_recent_txs():
    async with aiohttp.ClientSession() as session:
        async with session.get(MEMPOOL_API) as resp:
            return await resp.json()

async def monitor_general_btc_whales():
    global SEEN_TX
    logging.info("🔍 BTC Whale tracker started.")
    while True:
        try:
            btc_price = await fetch_btc_price()
            txs = await fetch_recent_txs()
            for tx in txs:
                txid = tx.get("txid")
                if txid in SEEN_TX:
                    continue

                total_vbytes = tx.get("vsize", 0)
                total_fee = tx.get("fee", 0)
                value_btc = tx.get("value", 0) / 1e8
                value_usd = round(value_btc * btc_price)

                if value_usd >= BTC_WHALE_THRESHOLD:
                    SEEN_TX.add(txid)
                    message = (
                        f"🐳 BTC Whale Alert!\n"
                        f"TXID: `{txid}`\n"
                        f"💰 Value: {value_btc:.2f} BTC (~${value_usd:,})\n"
                        f"🔍 Size: {total_vbytes} vbytes\n"
                        f"⛽ Fee: {total_fee} sats"
                    )
                    if bot and GROUP_ID:
                        await bot.send_message(chat_id=GROUP_ID, text=message)
                    logging.info(f"Whale BTC TX: {value_usd} USD")

        except Exception as e:
            logging.error(f"BTC whale monitor error: {e}")
        await asyncio.sleep(60)