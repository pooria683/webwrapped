"""Stable, obviously synthetic data for previews and tests."""
import random
from datetime import datetime, timedelta, timezone

from . import Visit

SITES = [
 ("github.com", "Pull requests", "dev"), ("stackoverflow.com/questions/11227809", "Why is processing sorted array faster?", "dev"),
 ("youtube.com/watch?v=demo", "Watched Tiny Desk Concert", "video"), ("bbc.co.uk/news", "BBC News", "news"),
 ("seriouseats.com/recipes", "The best roast potatoes", "food"), ("reddit.com/r/space", "Space", "social"),
 ("wikipedia.org/wiki/Octopus", "Octopus", "learning"), ("amazon.co.uk", "Shopping", "shopping")]

def generate(year: int, count: int = 1450) -> list[Visit]:
    rng = random.Random(year); start = datetime(year, 1, 2, 0, tzinfo=timezone.utc); out = []
    for i in range(count):
        day = rng.randrange(0, 360); hour = rng.choices(range(24), weights=[2]*6+[3]*3+[8]*14+[4], k=1)[0]
        host, title, _ = rng.choices(SITES, weights=[22,14,18,10,9,11,6,10], k=1)[0]
        out.append(Visit(start + timedelta(days=day, hours=hour, minutes=rng.randrange(60)), "https://"+host, title, "demo"))
    questions = ["how do octopuses dream", "is it too late to make pancakes", "why is the moon orange"]
    for i,q in enumerate(questions*4): out.append(Visit(start+timedelta(days=20*i, hours=1), "https://google.com/search?q="+q.replace(" ", "+"), q, "takeout-search"))
    return sorted(out, key=lambda v: v.date)
