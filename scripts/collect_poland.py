"""Collect weekly BondSpot fixings (resumable) and fit the Polish curves.

    python scripts/collect_poland.py collect     # download missing weeks (about 1 s each)
    python scripts/collect_poland.py fit         # fit NSS curves -> data/processed/pl_*
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from firv.data import poland  # noqa: E402

if __name__ == "__main__":
    what = sys.argv[1:] or ["collect", "fit"]
    if "collect" in what:
        n = poland.collect(log=lambda m: print(m, flush=True))
        print(f"weekly fixings available: {n}", flush=True)
    if "fit" in what:
        par, stats = poland.save_outputs()
        print(par.tail(3).round(3).to_string())
        print(stats.tail(3).round(2).to_string())
