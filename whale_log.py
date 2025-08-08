# whale_log.py
import json, os, datetime

LOG_PATH = "whale_log.jsonl"

def log_event(chain: str, message: str):
    entry = {
        "ts": datetime.datetime.utcnow().isoformat() + "Z",
        "chain": chain.upper(),
        "message": message
    }
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

def read_events(hours: int = 24):
    """Return entries from the last `hours` hours."""
    if not os.path.exists(LOG_PATH):
        return []
    cutoff = datetime.datetime.utcnow() - datetime.timedelta(hours=hours)
    out = []
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        for line in f:
            try:
                e = json.loads(line)
                ts = datetime.datetime.fromisoformat(e["ts"].replace("Z",""))
                if ts >= cutoff:
                    out.append(e)
            except Exception:
                continue
    return out