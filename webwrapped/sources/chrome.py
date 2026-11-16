"""Chromium History SQLite reader."""
import shutil
import sqlite3
import tempfile
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path

from webwrapped import Visit

_CHROME_EPOCH = datetime(1601, 1, 1, tzinfo=timezone.utc)

@contextmanager
def copied_db(path):
    with tempfile.TemporaryDirectory(prefix="webwrapped-") as d:
        target = Path(d) / "History"
        shutil.copy2(path, target)
        yield target

def read(path) -> list[Visit]:
    with copied_db(path) as copy:
        con = sqlite3.connect(f"file:{copy}?mode=ro", uri=True)
        try:
            rows = con.execute("SELECT v.visit_time,u.url,u.title FROM visits v JOIN urls u ON u.id=v.url ORDER BY v.visit_time")
            return [Visit(_CHROME_EPOCH + timedelta(microseconds=int(t)), url, title or "", "chrome") for t, url, title in rows]
        finally:
            con.close()
