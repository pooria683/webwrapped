import hashlib
import json

from webwrapped.demo_data import generate
from webwrapped.insights import build
from webwrapped.merge import merge, normalize_url
from webwrapped.render import render


def test_deterministic_stats_and_story():
    from pathlib import Path
    stats = build(merge(generate(2025, 50)), 2025)
    golden = Path(__file__).parent / "golden"
    assert json.dumps(stats, indent=2, sort_keys=True, ensure_ascii=False) + "\n" == (golden / "demo_stats.json").read_text()
    assert hashlib.sha256(render(stats).encode()).hexdigest() + "\n" == (golden / "demo_story.sha256").read_text()

def test_core_insights():
    stats=build(generate(2025,200),2025)
    assert stats['total_visits']>=200 and stats['top_sites'] and stats['longest_streak_days']>0
    assert stats['searches']['after_midnight']

def test_normalize_and_dedupe():
    assert normalize_url('HTTPS://WWW.Example.com/a/?utm_source=x')=='https://example.com/a?utm_source=x'
