"""Browser history readers and default-path discovery."""
import os
import sys
from pathlib import Path


def default_paths() -> dict[str, list[Path]]:
    home = Path.home()
    if sys.platform == "darwin":
        chromium = home / "Library/Application Support"
        firefox = home / "Library/Application Support/Firefox/Profiles"
    elif os.name == "nt":
        local = Path(os.environ.get("LOCALAPPDATA", home))
        roaming = Path(os.environ.get("APPDATA", home))
        chromium, firefox = local, roaming / "Mozilla/Firefox/Profiles"
    else:
        chromium, firefox = home / ".config", home / ".mozilla/firefox"
    chrome_roots = [chromium / p for p in (
            "google-chrome", "chromium", "BraveSoftware/Brave-Browser", "microsoft-edge",
            "vivaldi", "Google/Chrome", "Microsoft Edge", "Arc/User Data")]
    chrome_histories = []
    for root in chrome_roots:
        chrome_histories.extend(root.glob("*/History"))
    downloads = home / "Downloads"
    candidates = {
        "chrome": chrome_histories + [chromium / p for p in (
            "google-chrome/Default/History", "chromium/Default/History",
            "BraveSoftware/Brave-Browser/Default/History", "microsoft-edge/Default/History",
            "vivaldi/Default/History", "Google/Chrome/Default/History",
            "Microsoft Edge/Default/History", "Arc/User Data/Default/History")],
        "firefox": list(firefox.glob("*/places.sqlite")) if firefox.exists() else [],
        "safari": [home / "Library/Safari/History.plist", home / "Library/Safari/History.db"],
        "takeout": sorted(downloads.glob("takeout-*.zip")) if downloads.exists() else [],
    }
    return {k: sorted({p for p in ps if p.exists()}) for k, ps in candidates.items()}
