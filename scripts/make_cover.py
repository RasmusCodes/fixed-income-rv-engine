"""Cover image for the project page: the six par curves on the latest common date.

    python scripts/make_cover.py OUT.png
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from firv import market as M  # noqa: E402
from firv.curves import fit  # noqa: E402
from firv.research.report import INK, INK2, MUTED, SERIES, setup_mpl  # noqa: E402

NAMES = {"US": "United States", "DE": "Germany", "FR": "France", "UK": "United Kingdom", "JP": "Japan", "PL": "Poland"}


def main(out: str):
    plt = setup_mpl()
    fig, ax = plt.subplots(figsize=(12, 6.75), dpi=150)
    ends = []
    for i, m in enumerate(["US", "DE", "FR", "UK", "JP", "PL"]):
        d = M.nearest_date(m, "2100-01-01")
        res = fit("nss", M.observations(m, d))
        tmax = min(30.0, max(res.data.tenors))
        t = np.exp(np.linspace(np.log(1.0), np.log(tmax), 120))
        y = np.array([res.curve.par_yield(float(x), M.MARKETS[m].freq) for x in t]) * 100
        ax.plot(t, y, color=SERIES[i], lw=3.2, solid_capstyle="round")
        ends.append([t[-1], y[-1], m, SERIES[i]])
    # direct labels at the right end, nudged apart vertically
    ends.sort(key=lambda e: e[1])
    for k in range(1, len(ends)):
        if ends[k][1] - ends[k - 1][1] < 0.17:
            ends[k][1] = ends[k - 1][1] + 0.17
    for x, y, m, c in ends:
        ax.text(31.5 if x > 25 else x * 1.06, y, NAMES[m], color=INK2, fontsize=15, va="center", fontweight="semibold")
    ax.set_xscale("log")
    ax.set_xticks([1, 2, 3, 5, 7, 10, 20, 30], ["1y", "2y", "3y", "5y", "7y", "10y", "20y", "30y"])
    ax.tick_params(labelsize=13, colors=MUTED)
    ax.set_xlim(0.95, 60)
    ax.set_ylabel("par yield, %", fontsize=13, color=INK2)
    ax.set_title("Government bond par curves, fitted with Nelson-Siegel-Svensson", fontsize=17, color=INK, loc="left", pad=14)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    print("wrote", out)


if __name__ == "__main__":
    main(sys.argv[1])
