import aiohttp
import asyncio
import math
from datetime import datetime, timezone
from price_fetcher import get_top_50_crypto_prices
# Coins to evaluate (CoinGecko IDs)
COINS = [
    "bitcoin", "ethereum", "ripple", "solana", "cardano", "dogecoin",
    "polygon-pos", "tron", "litecoin", "chainlink", "avalanche-2",
    "polkadot", "uniswap", "near", "internet-computer"
]

API_BASE = "https://api.coingecko.com/api/v3"
def format_top_cryptos():
    coins = get_top_50_crypto_prices()

    if not coins:
        return "⚠️ Unable to fetch data at this time."

    message = "📊 *Top 10 by Market Cap (Live)*\n\n"
    for i, coin in enumerate(coins[:10], start=1):  # Limit to top 10
        name = coin["name"]
        symbol = coin["symbol"].upper()
        price = f"${coin['price']:.2f}"
        change = coin["price_change_24h"]
        emoji = "🟢" if change >= 0 else "🔴"
        change_text = f"{emoji} {change:.2f}%"

        message += f"{i}. *{name}* ({symbol})\nPrice: {price}\n24h Change: {change_text}\n\n"

    return message

# ---------- Indicator helpers (no numpy/pandas needed) ----------

def ema(values, period):
    if not values or len(values) < period:
        return None
    k = 2 / (period + 1)
    e = values[0]
    for v in values[1:]:
        e = v * k + e * (1 - k)
    return e

def rsi(values, period=14):
    if len(values) < period + 1:
        return None
    gains, losses = 0.0, 0.0
    # seed
    for i in range(1, period + 1):
        delta = values[i] - values[i - 1]
        if delta >= 0:
            gains += delta
        else:
            losses -= delta
    avg_gain = gains / period
    avg_loss = losses / period if losses != 0 else 1e-9

    # Wilder's smoothing
    for i in range(period + 1, len(values)):
        delta = values[i] - values[i - 1]
        gain = max(delta, 0.0)
        loss = max(-delta, 0.0)
        avg_gain = (avg_gain * (period - 1) + gain) / period
        avg_loss = (avg_loss * (period - 1) + loss) / period

    rs = avg_gain / (avg_loss if avg_loss != 0 else 1e-9)
    return 100 - (100 / (1 + rs))

def percent_change(a, b):
    if b == 0:
        return 0.0
    return (a - b) / b * 100.0

# ---------- Fetch & score ----------

async def fetch_market_chart(session, coin_id, days=2, interval="hourly"):
    url = f"{API_BASE}/coins/{coin_id}/market_chart?vs_currency=usd&days={days}&interval={interval}"
    async with session.get(url, timeout=20) as resp:
        if resp.status != 200:
            return None
        data = await resp.json()
        # Each item is [timestamp(ms), value]
        prices = [p[1] for p in (data.get("prices") or [])]
        vols = [v[1] for v in (data.get("total_volumes") or [])]
        return prices, vols

def score_signal(coin_id, prices, vols):
    """
    Returns a dict with:
      risk (1-10), reason list, metrics
    Lower = safer.
    """
    reasons = []
    if len(prices) < 30 or len(vols) < 30:
        return None

    last = prices[-1]
    prev_24 = prices[-25] if len(prices) > 25 else prices[0]
    chg_24h = percent_change(last, prev_24)

    ema20 = ema(prices[-60:], 20) if len(prices) >= 60 else ema(prices, 20)
    ema50 = ema(prices[-120:], 50) if len(prices) >= 120 else ema(prices, 50)
    _rsi = rsi(prices, 14)

    vol_now = vols[-1]
    vol_avg7 = sum(vols[-8:-1]) / 7 if len(vols) >= 8 else sum(vols) / max(1, len(vols))
    vol_surge = (vol_now / vol_avg7) if vol_avg7 > 0 else 1.0

    # Base risk from volatility (stddev proxy using high-low window)
    window = prices[-24:]
    mean = sum(window) / len(window)
    var = sum((x - mean) ** 2 for x in window) / len(window)
    vol_proxy = math.sqrt(var) / mean if mean > 0 else 0.02  # relative volatility

    # Start with volatility scaled to 1–10
    risk = min(10, max(1, 1 + vol_proxy * 60))  # tune factor

    # Trend adjustments
    if ema20 and ema50:
        if ema20 > ema50:
            risk -= 0.7  # uptrend a bit safer for longs
            reasons.append("EMA20>EMA50 (uptrend)")
        else:
            risk += 0.7
            reasons.append("EMA20<EMA50 (downtrend)")

    # RSI extremes
    if _rsi is not None:
        if _rsi > 70:
            risk += 0.6; reasons.append(f"RSI={_rsi:.0f} (overbought)")
        elif _rsi < 30:
            risk += 0.4; reasons.append(f"RSI={_rsi:.0f} (oversold / reversal risk)")
        else:
            reasons.append(f"RSI={_rsi:.0f}")

    # Volume surge = more risk but more opportunity
    if vol_surge > 1.6:
        risk += 0.8; reasons.append(f"Volume x{vol_surge:.1f} (surge)")

    # Big 24h moves add risk
    if abs(chg_24h) >= 6:
        risk += 0.7; reasons.append(f"24h move {chg_24h:.1f}%")

    # Clamp
    risk = float(min(10, max(1, round(risk, 1))))

    return {
        "coin": coin_id,
        "risk": risk,
        "chg_24h": chg_24h,
        "ema20": ema20,
        "ema50": ema50,
        "rsi": _rsi,
        "vol_surge": vol_surge,
        "last": last,
        "reasons": reasons
    }

def coin_emoji(coin_id):
    mapping = {
        "bitcoin": "₿", "ethereum": "♦", "ripple": "✦", "solana": "◎",
        "cardano": "◈", "dogecoin": "Ð", "polygon-pos": "⬣", "tron": "Ŧ",
        "litecoin": "Ł", "chainlink": "🔗", "avalanche-2": "A", "polkadot": "●",
        "uniswap": "🦄", "near": "NEAR", "internet-computer": "ICP"
    }
    return mapping.get(coin_id, "•")

async def build_signals(n_safe=1, n_risky=1):
    """
    Returns (safe_list, risky_list) sorted by risk asc/desc respectively.
    Each item is a dict from score_signal().
    """
    results = []
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_market_chart(session, c) for c in COINS]
        charts = await asyncio.gather(*tasks, return_exceptions=True)

    for coin_id, chart in zip(COINS, charts):
        if isinstance(chart, Exception) or chart is None:
            continue
        prices, vols = chart
        scored = score_signal(coin_id, prices, vols)
        if scored:
            results.append(scored)

    if not results:
        return [], []

    # Sort
    by_safe = sorted(results, key=lambda x: (x["risk"], -x["chg_24h"]))
    by_risk = sorted(results, key=lambda x: (-x["risk"], -abs(x["chg_24h"])))

    return by_safe[:n_safe], by_risk[:n_risky]

def format_signal_block(title, items):
    lines = [f"<b>{title}</b>"]
    for s in items:
        em = coin_emoji(s["coin"])
        chg = s["chg_24h"]
        rsi_v = s["rsi"]
        reasons = " | ".join(s["reasons"][:3]) if s["reasons"] else "-"
        lines.append(
            f"{em} <b>{s['coin'].title()}</b> — Risk <b>{s['risk']:.1f}/10</b> | "
            f"24h {chg:+.2f}% | RSI {rsi_v:.0f} | {reasons}"
        )
    return "\n".join(lines)

def compose_alert_text(safe, risky):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    parts = [
        "⚡️ <b>DeityTradePro Smart Signals</b>",
        f"🕒 {now}",
        "",
        format_signal_block("🛡 SAFE PICKS", safe) if safe else "🛡 SAFE PICKS\n(no candidates)",
        "",
        format_signal_block("⚠️ HIGH-RISK SETUPS", risky) if risky else "⚠️ HIGH-RISK SETUPS\n(no candidates)",
        "",
        "Notes: Risk score considers trend (EMA), RSI, volume surge, 24h move & volatility."
    ]
    return "\n".join(parts)

async def generate_signal_text(n_safe=1, n_risky=1):
    safe, risky = await build_signals(n_safe=n_safe, n_risky=n_risky)
    return compose_alert_text(safe, risky)