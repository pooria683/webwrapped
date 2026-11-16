"""Firefox places.sqlite reader."""
import sqlite3
from datetime import datetime, timezone

from webwrapped import Visit

from .chrome import copied_db


def read(path) -> list[Visit]:
    with copied_db(path) as copy:
        con = sqlite3.connect(f"file:{copy}?mode=ro", uri=True)
        try:
            rows = con.execute("SELECT v.visit_date,p.url,p.title FROM moz_historyvisits v JOIN moz_places p ON p.id=v.place_id ORDER BY v.visit_date")
            return [Visit(datetime.fromtimestamp(int(t)/1_000_000, timezone.utc), url, title or "", "firefox") for t, url, title in rows if t]
        finally:
            con.close()
