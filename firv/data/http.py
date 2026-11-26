"""Polite HTTP with an on-disk raw cache.

Every downloaded file is stored under ``data/raw/<source>/`` with the URL it came from and
the retrieval time in ``_manifest.json``, so any number in the project can be traced to a
file and a URL. Nothing is re-downloaded while the cached copy is younger than
``max_age_days``.
"""
from __future__ import annotations

import datetime as dt
import json
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
RAW = DATA / "raw"
INBOX = DATA / "inbox"
PROCESSED = DATA / "processed"
USER_AGENT = "fixed-income-rv-engine research script (python-requests)"

_session = None


def session() -> requests.Session:
    global _session
    if _session is None:
        _session = requests.Session()
        _session.headers["User-Agent"] = USER_AGENT
    return _session


def _manifest(folder: Path) -> dict:
    p = folder / "_manifest.json"
    return json.loads(p.read_text()) if p.exists() else {}


def _write_manifest(folder: Path, man: dict):
    (folder / "_manifest.json").write_text(json.dumps(man, indent=1, sort_keys=True))


def fetch(source: str, name: str, url: str, params: dict | None = None,
          max_age_days: float = 1.0, timeout: float = 90.0, retries: int = 3,
          pause: float = 0.5) -> Path:
    """Download ``url`` to data/raw/<source>/<name> unless a fresh copy exists."""
    folder = RAW / source
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / name
    man = _manifest(folder)
    if target.exists() and name in man:
        age = (dt.datetime.now(dt.timezone.utc) -
               dt.datetime.fromisoformat(man[name]["retrieved"])).total_seconds() / 86400
        if age < max_age_days:
            return target
    last = None
    for attempt in range(retries):
        try:
            r = session().get(url, params=params, timeout=timeout)
            if r.status_code == 200:
                target.write_bytes(r.content)
                man[name] = {"url": r.url, "retrieved": dt.datetime.now(dt.timezone.utc).isoformat(),
                             "bytes": len(r.content)}
                _write_manifest(folder, man)
                time.sleep(pause)
                return target
            last = f"HTTP {r.status_code}"
            if r.status_code in (403, 404):
                break
        except requests.RequestException as exc:  # network hiccup: retry
            last = f"{type(exc).__name__}: {exc}"
        time.sleep(2.0 * (attempt + 1))
    if target.exists():
        return target            # stale but usable
    raise RuntimeError(f"download failed for {url}: {last}")


def inbox_file(pattern: str) -> Path | None:
    """Newest file in data/inbox matching a glob pattern (user-downloaded files)."""
    hits = sorted(INBOX.glob(pattern), key=lambda p: p.stat().st_mtime)
    return hits[-1] if hits else None
