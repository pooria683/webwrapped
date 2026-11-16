from collections import Counter


def analyze(visits):
    searches = [v for v in visits if v.source == "takeout-search"]
    counts = Counter(v.title.strip() for v in searches if v.title.strip())
    late = Counter(v.title.strip() for v in searches if v.title.strip() and 0 <= v.date.hour < 5)
    pack = lambda c: [{"query": k, "count": n} for k, n in sorted(c.items(), key=lambda x: (-x[1], x[0].lower()))[:10]]
    return {"total": len(searches), "top": pack(counts), "after_midnight": pack(late)}
