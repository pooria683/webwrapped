"""Safari plist reader (with History.db support for current Safari)."""
import plistlib
import sqlite3
from datetime import datetime, timedelta, timezone

from webwrapped import Visit

from .chrome import copied_db

_APPLE_EPOCH = datetime(2001, 1, 1, tzinfo=timezone.utc)

def read(path) -> list[Visit]:
    if str(path).endswith(".db"):
        with copied_db(path) as copy:
            con = sqlite3.connect(f"file:{copy}?mode=ro", uri=True)
            try:
                rows = con.execute("SELECT v.visit_time,i.url,i.title FROM history_visits v JOIN history_items i ON i.id=v.history_item")
                return [Visit(_APPLE_EPOCH + timedelta(seconds=float(t)), u, title or "", "safari") for t, u, title in rows]
            finally: con.close()
    with open(path, "rb") as f:
        data = plistlib.load(f)
    rows = data.get("WebHistoryDates", data if isinstance(data, list) else [])
    out = []
    for item in rows:
        raw = item.get("lastVisitedDate", item.get("date", 0))
        dt = raw if isinstance(raw, datetime) else _APPLE_EPOCH + timedelta(seconds=float(raw))
        out.append(Visit(dt.replace(tzinfo=dt.tzinfo or timezone.utc), item.get("URLString", item.get("url", "")), item.get("title", ""), "safari"))
    return out
