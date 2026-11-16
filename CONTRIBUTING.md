# Contributing

Thanks for making webwrapped better. Keep the core dependency-free, deterministic, and local.

## Development

```bash
python -m pip install -e '.[dev]'
pytest
ruff check webwrapped tests
```

## Add a browser source

1. Add `webwrapped/sources/name.py` with `read(path) -> list[Visit]`.
2. Copy live SQLite databases before reading (use `copied_db`).
3. Set a stable source name and timezone-aware UTC dates.
4. Add default paths in `sources/__init__.py` and a tiny synthetic fixture test.
5. Never make a network request or collect telemetry.

## Add category heuristics

Extend `CATEGORIES` in `webwrapped/insights/eras.py` with narrowly targeted domain fragments. Add a test, avoid brand assumptions, and explain ambiguous classifications in the PR. Community-maintained categories are a central part of this project.
