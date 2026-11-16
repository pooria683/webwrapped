"""Find long, diverse browsing sessions (30 minute inactivity boundary)."""
from webwrapped.merge import domain


def find(visits, limit=5):
    sessions, current = [], []
    for v in sorted(visits, key=lambda x: x.date):
        if current and (v.date - current[-1].date).total_seconds() > 1800:
            sessions.append(current); current = []
        current.append(v)
    if current: sessions.append(current)
    result = []
    for s in sessions:
        domains = list(dict.fromkeys(domain(v.url) for v in s))
        if len(domains) >= 2:
            result.append({"started_at": s[0].date.isoformat(), "minutes": round((s[-1].date-s[0].date).total_seconds()/60), "visits": len(s), "domains": len(domains), "from": domains[0], "to": domains[-1]})
    return sorted(result, key=lambda x: (-x["domains"], -x["visits"], x["started_at"]))[:limit]
