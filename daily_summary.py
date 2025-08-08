# daily_summary.py
from whale_log import read_events
from config import GROUP_ID, BOT  # BOT is your aiogram Bot instance

def _fmt_counts(entries):
    by_chain = {"ETH":0, "BTC":0, "XRP":0}
    for e in entries:
        by_chain[e.get("chain","")] = by_chain.get(e.get("chain",""), 0) + 1
    return by_chain

async def daily_whale_summary():
    entries = read_events(hours=24)
    counts = _fmt_counts(entries)

    if not entries:
        text = (
            "📊 **Daily Whale Summary (last 24h)**\n"
            "No whale events logged in the last 24 hours."
        )
        await BOT.send_message(GROUP_ID, text)
        return

    # Show last 6 notable lines (most recent last)
    tail = entries[-6:]
    lines = [f"• [{e['chain']}] {e['message']}" for e in tail]

    text = (
        "📊 **Daily Whale Summary (last 24h)**\n"
        f"• ETH events: {counts.get('ETH',0)}\n"
        f"• BTC events: {counts.get('BTC',0)}\n"
        f"• XRP events: {counts.get('XRP',0)}\n\n"
        "Recent activity:\n" + "\n".join(lines)
    )
    await BOT.send_message(GROUP_ID, text)