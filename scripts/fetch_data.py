"""Download and parse every data source into data/processed (parquet + json metadata).

    python scripts/fetch_data.py            # everything
    python scripts/fetch_data.py us uk      # only some groups

Sources that refuse scripts (Bank of England, Banque de France, FRED) are read from files
saved in data/inbox; see data/inbox/DOWNLOAD_LIST.md.
"""
from __future__ import annotations

import sys
import time
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from firv.data import loaders as L  # noqa: E402

GROUPS = {
    "us": [L.load_us_par, L.load_us_real, L.load_gsw, L.load_gsw_tips, L.load_sofr],
    "de": [L.load_bundesbank, L.load_bundesbank_params],
    "ea": [lambda: L.load_ecb_curve("A"), lambda: L.load_ecb_curve("C"),
           lambda: L.load_ecb_spot("A"), L.load_estr],
    "fr": [L.load_france_tec],
    "uk": [lambda: L.load_uk("nominal"), lambda: L.load_uk("real"),
           lambda: L.load_uk("inflation"), lambda: L.load_uk("ois")],
    "jp": [L.load_japan],
    "fred": [L.load_fred_swaps, L.load_fred_moodys],
    "macro": [L.load_policy_rates, L.load_oecd_rates, L.load_cpi, L.load_oecd_fiscal, L.load_fx],
}


def main(groups):
    for g in groups:
        for fn in GROUPS[g]:
            t0 = time.time()
            try:
                out = fn()
                panels = out if isinstance(out, tuple) else (out,)
                for p in panels:
                    p.save()
                    d = p.data
                    print(f"[{g}] {p.name:22s} {d.shape[0]:6d} x {d.shape[1]:3d}  "
                          f"{d.index.min():%Y-%m-%d} .. {d.index.max():%Y-%m-%d}  "
                          f"({time.time() - t0:.1f}s)", flush=True)
            except Exception as exc:  # report and continue with the other sources
                print(f"[{g}] FAILED {getattr(fn, '__name__', 'lambda')}: {type(exc).__name__}: {exc}", flush=True)
                traceback.print_exc(limit=2)


if __name__ == "__main__":
    main(sys.argv[1:] or list(GROUPS))
