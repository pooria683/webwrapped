"""Streaming Google Takeout activity reader, including raw ZIP files."""
import codecs
import json
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from webwrapped import Visit

_FILES = ("My Activity/Chrome/MyActivity.json", "My Activity/Search/MyActivity.json")

def _objects(stream):
    """Yield JSON objects from a top-level array without retaining the whole file."""
    decoder, buf, pos, started = json.JSONDecoder(), "", 0, False
    utf8 = codecs.getincrementaldecoder("utf-8")("replace")
    while True:
        chunk = stream.read(65536)
        if chunk:
            buf += utf8.decode(chunk if isinstance(chunk, bytes) else chunk.encode())
        else:
            buf += utf8.decode(b"", final=True)
        while True:
            while pos < len(buf) and (buf[pos].isspace() or buf[pos] in "[,]"):
                started = started or buf[pos] == "["; pos += 1
            if pos < len(buf) and buf[pos] == "]": return
            try:
                obj, end = decoder.raw_decode(buf, pos)
            except json.JSONDecodeError:
                break
            if isinstance(obj, dict): yield obj
            pos = end
        if pos > 65536: buf, pos = buf[pos:], 0
        if not chunk: return

def _parse_date(value):
    try: return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except (ValueError, AttributeError): return None

def _item(item, source):
    dt = _parse_date(item.get("time") or item.get("time_usec"))
    if not dt: return None
    title, url = str(item.get("title", "")), str(item.get("titleUrl", ""))
    if source == "search":
        query = re.sub(r"^(Searched for|Visited)\s+", "", title, flags=re.IGNORECASE)
        if not url: url = "https://www.google.com/search?q=" + query.replace(" ", "+")
        title = query
    return Visit(dt, url, title, "takeout-search" if source == "search" else "takeout-chrome")

def _read_stream(stream, source):
    return [v for item in _objects(stream) if (v := _item(item, source))]

def read(path) -> list[Visit]:
    path = Path(path); out = []
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as z:
            for name in z.namelist():
                matched = next((f for f in _FILES if name.replace("Takeout/", "").endswith(f)), None)
                if matched:
                    with z.open(name) as stream: out.extend(_read_stream(stream, "search" if "/Search/" in matched else "chrome"))
    elif path.is_dir():
        for f in path.rglob("MyActivity.json"):
            if "Chrome" in f.parts or "Search" in f.parts:
                with open(f, "rb") as stream: out.extend(_read_stream(stream, "search" if "Search" in f.parts else "chrome"))
    else:
        with open(path, "rb") as stream: out.extend(_read_stream(stream, "search" if "Search" in str(path) else "chrome"))
    return out
