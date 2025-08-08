# btc_wallet_watcher.py
import aiohttp
import asyncio
import json
import logging
from aiogram import Bot
from config import GROUP_ID

# Will be set from main.py
BOT: Bot | None = None

TRACKED_FILE = "tracked_btc_wallets.json"
SEEN_FILE = "btc_wallet_seen.json"

# Blockchair address dashboard with tx details
ADDR_API = "https://api.blockchair.com/bitcoin/dashboards/address/{}?transaction_details=true"

async def _load_tracked():
    """Return a flat list of wallets with address, label, tier."""
    try:
        with open(TRACKED_FILE, "r") as f:
            data = json.load(f)
        wallets = []
        for tier, items in data.items():
            for w in items:
                addr = w.get("address") or w.get("addr")
                if not addr:
                    continue
                label = w.get("label") or f"{addr[:6]}...{addr[-4:]}"
                wallets.append({"address": addr, "label": label, "tier": tier})
        return wallets
    except Exception:
        return []

def _load_seen():
    try:
        with open(SEEN_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def _save_seen(seen: dict):
    with open(SEEN_FILE, "w") as f:
        json.dump(seen, f)

async def _fetch_latest_tx(session: aiohttp.ClientSession, address: str) -> str | None:
    """Return the latest txid for the address, or None."""
    url = ADDR_API.format(address)
    async with session.get(url) as resp:
        if resp.status != 200:
            return None
        data = await resp.json()
        try:
            txs = data["data"][address]["transactions"]
            return txs[0] if txs else None
        except Exception:
            return None

async def monitor_btc_wallets(poll_seconds: int = 20):
    logging.info("✅ BTC wallet watcher is live.")
    await asyncio.sleep(5)  # give bot time to init

    seen = _load_seen()

    async with aiohttp.ClientSession() as session:
        while True:
            try:
                wallets = await _load_tracked()
                for w in wallets:
                    addr = w["address"]
                    latest = await _fetch_latest_tx(session, addr)
                    if not latest:
                        continue
                    if seen.get(addr) == latest:
                        continue  # no change

                    # New activity for this wallet
                    seen[addr] = latest
                    _save_seen(seen)

                    tx_link = f"https://blockchair.com/bitcoin/transaction/{latest}"
                    text = (
                        f"👀 **BTC Wallet Watch — {w['tier'].upper()}**\n"
                        f"Label: {w['label']}\n"
                        f"Address: `{addr}`\n"
                        f"Latest tx: {latest}\n"
                        f"{tx_link}"
                    )

                    if BOT:
                        await BOT.send_message(
                            GROUP_ID, text,
                            disable_web_page_preview=True,
                            parse_mode="Markdown"
                        )
                    logging.info("BTC wallet alert sent for %s (%s)", w['label'], latest)

                await asyncio.sleep(poll_seconds)
            except Exception as e:
                logging.exception("BTC wallet watcher error: %s", e)
                await asyncio.sleep(poll_seconds)