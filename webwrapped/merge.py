"""URL normalization and deterministic cross-source de-duplication."""
from datetime import timezone
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from . import Visit

_TRACKING = {"fbclid", "gclid", "mc_cid", "mc_eid", "ref", "source"}

def normalize_url(url: str) -> str:
    try:
        p = urlsplit(url.strip())
        host = (p.hostname or "").lower().removeprefix("www.")
        if not host:
            return url.strip()
        port = f":{p.port}" if p.port and p.port not in (80, 443) else ""
        query = urlencode(sorted((k, v) for k, v in parse_qsl(p.query) if k.lower() not in _TRACKING))
        path = p.path.rstrip("/") or "/"
        return urlunsplit(((p.scheme or "https").lower(), host + port, path, query, ""))
    except (ValueError, UnicodeError):
        return url.strip()

def domain(url: str) -> str:
    try:
        return (urlsplit(url).hostname or "unknown").lower().removeprefix("www.")
    except ValueError:
        return "unknown"

def merge(visits: list[Visit]) -> list[Visit]:
    """Union sources, treating same normalized URL within two seconds as one visit."""
    out, seen = [], set()
    for v in sorted(visits, key=lambda x: (x.date, normalize_url(x.url), x.source)):
        dt = v.date.replace(tzinfo=v.date.tzinfo or timezone.utc).astimezone(timezone.utc)
        key = (normalize_url(v.url), round(dt.timestamp() / 2))
        if key not in seen:
            seen.add(key)
            out.append(Visit(dt, normalize_url(v.url), v.title or "", v.source))
    return out
