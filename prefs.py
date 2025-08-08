# prefs.py
import sqlite3

DB = "prefs.db"

def init():
    con = sqlite3.connect(DB)
    c = con.cursor()
    c.execute("""
      CREATE TABLE IF NOT EXISTS prefs(
        chat_id INTEGER PRIMARY KEY,
        risk TEXT DEFAULT 'med',
        n_safe INTEGER DEFAULT 3,
        n_risky INTEGER DEFAULT 2
      )
    """)
    con.commit(); con.close()

def get(chat_id):
    con = sqlite3.connect(DB); c = con.cursor()
    row = c.execute(
        "SELECT risk, n_safe, n_risky FROM prefs WHERE chat_id=?",
        (chat_id,)
    ).fetchone()
    con.close()
    return row or ('med', 3, 2)

def set(chat_id, **kw):
    con = sqlite3.connect(DB); c = con.cursor()
    c.execute("INSERT OR IGNORE INTO prefs(chat_id) VALUES(?)", (chat_id,))
    if 'risk'   in kw: c.execute("UPDATE prefs SET risk=?   WHERE chat_id=?", (kw['risk'], chat_id))
    if 'n_safe' in kw: c.execute("UPDATE prefs SET n_safe=? WHERE chat_id=?", (kw['n_safe'], chat_id))
    if 'n_risky'in kw: c.execute("UPDATE prefs SET n_risky=?WHERE chat_id=?", (kw['n_risky'], chat_id))
    con.commit(); con.close()