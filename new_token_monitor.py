# new_token_monitor.py
import os
import json
import time
import asyncio
import logging
from typing import Dict, List, Any, Optional

import aiohttp

"""
Monitors ETH whale wallets and alerts when they acquire a token
they did not hold before (i.e., a "new token" for that wallet).

Data source: Ethplorer (public 'freekey') for quick token inventory checks.
Rate limits are modest; we space requests politely.
"""

ETHPLORER_BASE = "https://api.ethplorer.io"
ETHPLORER_KEY = os.getenv("ETHPLORER_KEY", "freekey")  # can be replaced with your key

# Where we persist last-known token symbols per wallet
STATE_FILE = "whale_new_tokens_state.json"
# Optional: where your ETH whales are listed if not passed in
DEFAULT_WHALES_FILE = "eth_whales.json"

# These are injected by main.py
bot = None
GROUP_ID = None


# ---------- File helpers ----------
def _ensure_file(path: str, default: Any):
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump(default, f, indent=2)


def _load_json(path: str, default: Any):
    _ensure_file(path, default)
    with open(path, "r") as f:
        try:
            return json.load(f)
        except Exception:
            return default


def _save_json(path: str, data: Any):
    tmp = f"{path}.tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, path)


# ---------- API ----------
async def fetch_eth_tokens(session: aiohttp.ClientSession, address: str) -> List[str]:
    """
    Returns a list of token symbols (including 'ETH' if non-zero balance) currently held by the wallet.
    Uses Ethplorer: /getAddressInfo/{address}
    """
    url = f"{ETHPLORER_BASE}/getAddressInfo/{address}"
    params = {"apiKey": ETHPLORER_KEY}
    try:
        async with session.get(url, params=params, timeout=20) as resp:
            if resp.status != 200:
                logging.warning(f"Ethplorer non-200 for {address}: {resp.status}")
                return []
            data = await resp.json()

            symbols: List[str] = []

            # ETH balance
            eth_balance = data.get("ETH", {}).get("balance", 0)
            if eth_balance and eth_balance > 0:
                symbols.append("ETH")

            # ERC-20 tokens
            for t in data.get("tokens", []) or []:
                info = t.get("tokenInfo") or {}
                sym = (info.get("symbol") or "").strip()
                if sym:
                    # treat any positive (raw) balance as "holding"
                    raw_bal = t.get("balance", 0)
                    if raw_bal and float(raw_bal) > 0:
                        symbols.append(sym)

            # Deduplicate and sort for stability
            return sorted(set(symbols))

    except Exception as e:
        logging.exception(f"fetch_eth_tokens error for {address}: {e}")
        return []


def _etherscan_link(address: str) -> str:
    return f"https://etherscan.io/address/{address}"


async def _send_alert_new_token(wallet: str, new_symbols: List[str]):
    """
    Sends a Telegram alert for newly seen tokens.
    """
    if not bot or GROUP_ID is None:
        logging.error("Bot or GROUP_ID not injected; cannot send alert.")
        return

    pretty_wallet = f"{wallet[:6]}...{wallet[-4:]}"
    link = _etherscan_link(wallet)

    text = (
        "🚨 *Whale bought NEW token(s)*\n"
        f"👛 Wallet: `{pretty_wallet}`\n"
        f"🔗 {link}\n"
        f"🧩 Tokens: " + ", ".join(f"`{s}`" for s in new_symbols)
    )

    try:
        await bot.send_message(GROUP_ID, text, parse_mode="Markdown")
        logging.info(f"New-token alert sent for {wallet}: {new_symbols}")
    except Exception as e:
        logging.exception(f"send_message failed: {e}")


def _load_whales(whales_file: str) -> List[str]:
    """
    Attempts to load a list of ETH whale addresses from a JSON file.
    Expected format: ["0xabc...", "0xdef...", ...]
    """
    if not os.path.exists(whales_file):
        logging.warning(
            f"No whales file found at {whales_file}. "
            f"Create it or pass whales explicitly."
        )
        return []
    try:
        with open(whales_file, "r") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            logging.warning("Whales file not a list; ignoring.")
            return []
    except Exception as e:
        logging.exception(f"Failed to read whales file: {e}")
        return []


# ---------- Main loop ----------
async def monitor_new_tokens_eth(whales: Optional[List[str]] = None, poll_seconds: int = 300):
    """
    Main loop: for each whale, check current tokens and compare to last state.
    On any newly-added symbols, alert and update state.

    poll_seconds default: 5 minutes.
    """
    # state: { wallet_address_lower: ["ETH", "USDC", ...] }
    state: Dict[str, List[str]] = _load_json(STATE_FILE, {})

    if whales is None:
        whales = _load_whales(DEFAULT_WHALES_FILE)

    if not whales:
        logging.warning("No ETH whales configured for new-token monitor. Waiting...")
        await asyncio.sleep(30)
        return

    logging.info(f"Starting New-Token monitor for {len(whales)} whales...")

    async with aiohttp.ClientSession() as session:
        while True:
            cycle_start = time.time()
            changed_count = 0

            for w in whales:
                w_norm = w.lower().strip()
                if not w_norm.startswith("0x") or len(w_norm) != 42:
                    # skip non-ETH or malformed addresses
                    continue

                symbols_current = await fetch_eth_tokens(session, w_norm)
                if not symbols_current:
                    # Skip if fetch failed; try next time
                    await asyncio.sleep(0.5)
                    continue

                symbols_prev = state.get(w_norm, [])
                # new tokens = in current but not in prev
                new_syms = [s for s in symbols_current if s not in symbols_prev]

                if new_syms:
                    await _send_alert_new_token(w_norm, new_syms)
                    state[w_norm] = symbols_current
                    changed_count += 1

                # be polite to Ethplorer
                await asyncio.sleep(0.6)

            # persist state if anything changed
            if changed_count:
                _save_json(STATE_FILE, state)

            # sleep until next cycle (5 min by default)
            elapsed = time.time() - cycle_start
            sleep_for = max(poll_seconds - elapsed, 5)
            await asyncio.sleep(sleep_for)


# ---------- Public entry for main.py ----------
async def start_new_token_monitor(injected_bot, group_id, whales: Optional[List[str]] = None):
    """
    Entrypoint to be scheduled from main.py
    """
    global bot, GROUP_ID
    bot = injected_bot
    GROUP_ID = group_id
    await monitor_new_tokens_eth(whales=whales)