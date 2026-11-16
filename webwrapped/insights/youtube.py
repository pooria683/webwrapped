from collections import Counter
from urllib.parse import urlsplit


def analyze(visits):
    watched, channels = [], Counter()
    for v in visits:
        host = (urlsplit(v.url).hostname or "").lower()
        if "youtube.com" in host and ("/watch" in v.url or "youtu.be" in host): watched.append(v)
        # Takeout titles commonly look like "Watched Title"; channel URLs survive too.
        if "youtube.com/channel/" in v.url or "youtube.com/@" in v.url:
            channels[v.title or v.url.rstrip("/").split("/")[-1]] += 1
    return {"watch_url_visits": len(watched), "top_channels": [{"channel": k, "count": n} for k, n in channels.most_common(10)]}
