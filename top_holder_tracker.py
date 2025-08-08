# top_holder_tracker.py
import os
import json
import time
import asyncio
import logging
from typing import List, Dict, Any, Optional
import aiohttp

# ===== Config =====
WHALE_MIN_USD = 100_000  # alert threshold
BTC_HOLDERS_FILE = "top_holders_btc.json"
BTC_EXCHANGES_FILE = "exchanges_btc.json"
BTC_SEEN_FILE = "top_btc_seen.json"

# These will be injected from main.py so we reuse your existing bot/session
bot = None
GROUP_ID = None

# ===== Helpers =====
def _ensure_file(path: str, default):
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump(default, f, indent=2)

def _load_json(path: str, default):
    _ensure_file(path, default)
    with open(path, "r") as f:
        return json.load(f)

def _save_json(path: str, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

async def _get_btc_price_usd(session: aiohttp.ClientSession) -> Optional[float]:
    # Coingecko simple price (no API key)
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    try:
        async with session.get(url, timeout=15) as r:
            if r.status == 200:
                data = await r.json()
                return float(data["bitcoin"]["usd"])
    except Exception as e:
        logging.warning(f"[BTC price] fetch failed: {e}")
    return None

async def _get_address_txs(session: aiohttp.ClientSession, address: str) -> Optional[Dict[str, Any]]:
    # blockchain.info rawaddr returns recent txs and per-tx net 'result' in satoshis for this address.
    url = f"https://blockchain.info/rawaddr/{address}?limit=10"
    try:
        async with session.get(url, timeout=20) as r:
            if r.status == 200:
                return await r.json()
            else:
                logging.warning(f"[BTC] {address} rawaddr HTTP {r.status}")
    except Exception as e:
        logging.warning(f"[BTC] {address} rawaddr error: {e}")
    return None

def _format_btc(n_sats: int) -> float:
    return n_sats / 1e8

def _short(addr: str) -> str:
    return f"{addr[:6]}…{addr[-6:]}"

def _tx_to_exchange(txd: Dict[str, Any], exchange_addrs: set) -> bool:
    # If any output goes to a known exchange AND net result is negative (sending), mark True
    try:
        for o in txd.get("out", []):
            a = o.get("addr")
            if a and a in exchange_addrs:
                return True
    except Exception:
        pass
    return False

async def _send_alert(text: str):
    try:
        await bot.send_message(chat_id=GROUP_ID, text=text, parse_mode="HTML", disable_web_page_preview=True)
    except Exception as e:
        logging.exception(f"[Alert send] failed: {e}")

# ===== Main monitor =====
async def monitor_top_btc_holders():
    logging.info("Starting Top-Holder BTC monitor…")

    holders: List[str] = _load_json(BTC_HOLDERS_FILE, default=[
        # Seed with a few well-known large/old wallets — replace/expand as you like
        "1P5ZEDWTKTFGxQjZphgWPQUpe554WKDfHQ",  # (Binance cold wallet label commonly cited)
        "3LYJfcfHPXYJreMsASk2jkn69LWEYKzexb",  # (example large multi-sig)
        "1DiqLtKZZviDxzk7Kvr9mJ3gT6VZN1b3a6",  # (example large)
    ])
    exchanges: List[str] = _load_json(BTC_EXCHANGES_FILE, default=[
        # A minimal seed list; expand over time
        "1NDyJtNTjmwk5xPNhjgAMu4HDHigtobu1s",  # Coinbase (example commonly referenced)
        "3D2oetdNuZUqQHPJmcMDDHYoqkyNVsFk9r",  # Bitfinex cold (example)
    ])
    seen: Dict[str, float] = _load_json(BTC_SEEN_FILE, default={})
    exchange_set = set(exchanges)

    async with aiohttp.ClientSession() as session:
        btc_usd = await _get_btc_price_usd(session)
        if not btc_usd:
            # Retry once if price failed
            await asyncio.sleep(3)
            btc_usd = await _get_btc_price_usd(session)
        btc_usd = btc_usd or 60_000.0  # fallback

        while True:
            start_ts = time.time()
            for addr in holders:
                data = await _get_address_txs(session, addr)
                if not data:
                    continue

                txs = data.get("txs", [])
                for tx in txs:
                    # tx hash
                    tx_hash = tx.get("hash")
                    if not tx_hash:
                        continue
                    # skip if we've seen it
                    if tx_hash in seen:
                        continue

                    # net result for this address in satoshis (positive = net received; negative = net sent)
                    sats_result = tx.get("result", 0)
                    btc_amount = abs(_format_btc(sats_result))
                    usd_value = btc_amount * btc_usd

                    if usd_value >= WHALE_MIN_USD:
                        is_outflow = sats_result < 0
                        to_exch = _tx_to_exchange(tx, exchange_set) if is_outflow else False
                        direction = "RECEIVED" if not is_outflow else "SENT"
                        exch_note = " 🔁 <b>To Exchange</b>" if to_exch else ""
                        msg = (
                            f"🐋 <b>BTC Top Holder Activity</b>\n\n"
                            f"👛 Wallet: <code>{addr}</code>\n"
                            f"🔹 Direction: <b>{direction}</b>{exch_note}\n"
                            f"💸 Amount: <b>{btc_amount:,.4f} BTC</b> (~${usd_value:,.0f})\n"
                            f"🔗 Tx: https://www.blockchain.com/btc/tx/{tx_hash}\n"
                            f"🔎 Holder: {_short(addr)} | Price: ${btc_usd:,.0f}"
                        )
                        await _send_alert(msg)

                    # mark seen regardless to avoid repeats
                    seen[tx_hash] = time.time()

                # persist occasionally
                if len(seen) % 20 == 0:
                    _save_json(BTC_SEEN_FILE, seen)

                # be polite
                await asyncio.sleep(0.5)

            # persist end of cycle
            _save_json(BTC_SEEN_FILE, seen)

            # repeat every 5 minutes
            elapsed = time.time() - start_ts
            sleep_for = max(300 - elapsed, 5)
            await asyncio.sleep(sleep_for)

# Public entrypoint for main.py
async def start_top_holders_monitor(injected_bot, group_id):
    global bot, GROUP_ID
    bot = injected_bot
    GROUP_ID = group_id
    await monitor_top_btc_holders()