"""webwrapped: local-first browser history year in review."""
from dataclasses import dataclass
from datetime import datetime

__version__ = "0.1.0"

@dataclass(frozen=True, slots=True)
class Visit:
    date: datetime
    url: str
    title: str = ""
    source: str = ""
