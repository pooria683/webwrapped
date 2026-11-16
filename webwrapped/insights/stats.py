"""Main deterministic insights engine."""
from collections import Counter, defaultdict
from datetime import timedelta

from webwrapped.merge import domain

from . import eras, queries, rabbit_holes, youtube


def _rank(counter, field, limit=10):
    return [{field: k, "visits": n} for k, n in sorted(counter.items(), key=lambda x: (-x[1], x[0]))[:limit]]

def build(visits, year: int):
    visits = sorted((v for v in visits if v.date.year == year), key=lambda v: v.date)
    by_site = Counter(domain(v.url) for v in visits)
    days = defaultdict(set)
    pages = Counter()
    day_counts, hour_counts = Counter(), Counter()
    for v in visits:
        host = domain(v.url); days[host].add(v.date.date().isoformat())
        pages[(v.url, v.title)] += 1; day_counts[v.date.date().isoformat()] += 1; hour_counts[v.date.hour] += 1
    # Active-time estimate: five minutes per session singleton, capped at 30m between visits.
    seconds = 0
    for i, v in enumerate(visits):
        if i + 1 < len(visits): seconds += min(300, max(0, (visits[i+1].date-v.date).total_seconds()))
        else: seconds += 300
    active_days = sorted(day_counts)
    longest = run = 0; previous = None
    for raw in active_days:
        from datetime import date
        d = date.fromisoformat(raw)
        run = run + 1 if previous and d - previous == timedelta(days=1) else 1
        longest, previous = max(longest, run), d
    most_page = max(pages.items(), key=lambda x: (x[1], x[0][0])) if pages else (("", ""), 0)
    earliest = visits[0].date.date().isoformat() if visits else None
    latest = visits[-1].date.date().isoformat() if visits else None
    coverage = ((visits[-1].date-visits[0].date).days + 1) if visits else 0
    return {
        "year": year, "total_visits": len(visits), "estimated_hours": round(seconds/3600, 1),
        "active_days": len(active_days), "coverage_days": coverage, "first_visit": earliest, "last_visit": latest,
        "busiest_day": ({"date": day_counts.most_common(1)[0][0], "visits": day_counts.most_common(1)[0][1]} if day_counts else None),
        "busiest_hour": (min((h for h,n in hour_counts.items() if n == max(hour_counts.values())), default=None) if hour_counts else None),
        "night_owl_score": round(100 * sum(hour_counts[h] for h in range(5)) / len(visits), 1) if visits else 0,
        "top_sites": _rank(by_site, "site"),
        "loyal_sites": [{"site": k, "days_seen": len(v), "visits": by_site[k]} for k,v in sorted(days.items(), key=lambda x: (-len(x[1]), x[0]))[:10]],
        "most_revisited_page": {"url": most_page[0][0], "title": most_page[0][1], "visits": most_page[1]},
        "longest_streak_days": longest, "eras": eras.detect(visits), "rabbit_holes": rabbit_holes.find(visits),
        "searches": queries.analyze(visits), "youtube": youtube.analyze(visits),
        "source_counts": dict(sorted(Counter(v.source for v in visits).items())),
        "chromium_limited_hint": bool(visits and coverage <= 100 and any(v.source == "chrome" for v in visits)),
    }
