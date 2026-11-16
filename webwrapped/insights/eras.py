"""Deterministic weekly topic-phase detection."""
from collections import Counter

from webwrapped.merge import domain

CATEGORIES = {
    "dev": ("github", "stackoverflow", "gitlab", "npmjs", "pypi", "developer", "docs."),
    "video": ("youtube", "netflix", "vimeo", "twitch"),
    "social": ("reddit", "twitter", "x.com", "facebook", "instagram", "tiktok", "linkedin"),
    "news": ("news", "bbc.", "cnn.", "guardian", "reuters"),
    "shopping": ("amazon", "ebay", "etsy", "shop", "argos"),
    "food": ("recipe", "food", "allrecipes", "seriouseats", "deliveroo"),
    "music": ("spotify", "soundcloud", "bandcamp"),
    "learning": ("wikipedia", "coursera", "udemy", "khanacademy"),
}

def category(host: str) -> str:
    for name, needles in CATEGORIES.items():
        if any(n in host for n in needles): return name
    return "exploring"

def detect(visits):
    weeks = {}
    for v in visits:
        key = f"{v.date.isocalendar().year}-W{v.date.isocalendar().week:02d}"
        weeks.setdefault(key, Counter())[category(domain(v.url))] += 1
    winners = [(w, c.most_common(1)[0]) for w, c in sorted(weeks.items()) if c]
    eras, current = [], None
    for week, (cat, count) in winners:
        if current and current["category"] == cat:
            current["end_week"], current["visits"], current["weeks"] = week, current["visits"] + count, current["weeks"] + 1
        else:
            current = {"category": cat, "label": f"Your {cat.title()} Era", "start_week": week, "end_week": week, "weeks": 1, "visits": count}
            eras.append(current)
    return sorted((e for e in eras if e["weeks"] >= 2 or e["visits"] >= 8), key=lambda e: (-e["visits"], e["start_week"]))[:5]
