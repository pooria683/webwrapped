"""Command-line interface."""
import argparse
import json
import sys
import webbrowser
from datetime import datetime
from pathlib import Path

from .demo_data import generate
from .insights import build
from .merge import merge
from .render import render
from .sources import chrome, default_paths, firefox, safari, takeout


def parser():
    p = argparse.ArgumentParser(prog="webwrapped", description="Turn browser history into a private year-in-review story.")
    p.add_argument("path", nargs="?", help="Takeout ZIP, directory, or MyActivity.json")
    p.add_argument("--year", type=int, default=datetime.now().year)
    p.add_argument("--sources", help="Comma-separated: chrome,firefox,safari,takeout")
    p.add_argument("--demo", action="store_true", help="Use synthetic preview data")
    p.add_argument("--json", action="store_true", dest="as_json", help="Print full stats JSON")
    p.add_argument("--out", type=Path, default=Path("webwrapped-story.html"))
    p.add_argument("--redact", action="store_true", help="Hide site names on the share card")
    p.add_argument("--no-open", action="store_true", help="Do not open the generated story")
    p.add_argument("--version", action="version", version="webwrapped 0.1.0")
    return p

def collect(args):
    if args.demo: return generate(args.year)
    if args.path: return takeout.read(args.path)
    wanted = set((args.sources or "chrome,firefox,safari,takeout").split(","))
    found = default_paths(); visits = []
    readers = {"chrome": chrome.read, "firefox": firefox.read, "safari": safari.read, "takeout": takeout.read}
    for name, reader in readers.items():
        if name in wanted:
            for path in found.get(name, []):
                try: visits.extend(reader(path))
                except (OSError, ValueError) as exc: print(f"warning: could not read {path}: {exc}", file=sys.stderr)
    return visits

def terminal(stats):
    """Compact ANSI summary, with an automatic plain-text fallback."""
    color = sys.stdout.isatty() and not __import__("os").environ.get("NO_COLOR")
    bold, purple, reset = ("\033[1m", "\033[35m", "\033[0m") if color else ("", "", "")
    top = stats["top_sites"][:3]
    lines = [f"{bold}{purple}WEBWRAPPED {stats['year']}{reset}", "="*24, f"{stats['total_visits']:,} visits  |  ~{stats['estimated_hours']} hours", f"Night owl: {stats['night_owl_score']}%  |  Longest streak: {stats['longest_streak_days']} days", "", "Top sites"]
    lines += [f"  {i}. {x['site']} ({x['visits']:,})" for i,x in enumerate(top,1)]
    if stats["chromium_limited_hint"]: lines += ["", "Tip: Chromium keeps ~90 days. Add Google Takeout for your full year."]
    return "\n".join(lines)

def main(argv=None):
    args = parser().parse_args(argv)
    try: visits = merge(collect(args))
    except (OSError, ValueError, json.JSONDecodeError) as exc: parser().error(str(exc))
    stats = build(visits, args.year)
    if args.as_json:
        print(json.dumps(stats, indent=2, sort_keys=True, ensure_ascii=False)); return
    print(terminal(stats))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(render(stats, args.redact), encoding="utf-8")
    print(f"\nStory saved to {args.out.resolve()}")
    if not args.no_open: webbrowser.open(args.out.resolve().as_uri())
