"""Golden values from the Python engine for the JavaScript port's self-test.

Writes web/test/golden.js (window.GOLDEN = {...}). Inputs are fixed numbers written into
the file (one real curve snapshot per market type plus synthetic Svensson curves), so the
test does not depend on the data folder.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from firv.curves import CurveData, Svensson, bootstrap_par, fit  # noqa: E402
from firv.instruments import par_bond  # noqa: E402
from firv.risk import Leg, carry_roll, dv01, key_rate_dv01, scenario_pnl  # noqa: E402
from firv.strategies import butterfly, curve_trade  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "web" / "test" / "golden.js"

CASES = {
    # US Treasury par yields, 2026-11-20 (treasury.gov)
    "us_par": {"tenors": [1 / 12, 1.5 / 12, 2 / 12, 0.25, 4 / 12, 0.5, 1, 2, 3, 5, 7, 10, 20, 30],
               "values": [4.19, 4.26, 4.28, 4.32, 4.32, 4.38, 4.51, 4.63, 4.65, 4.71, 4.80, 4.92, 5.34, 5.31],
               "kind": "par", "freq": 2},
    # French TEC, 2026-11-20 (Banque de France)
    "fr_par": {"tenors": [1, 2, 3, 5, 7, 10, 15, 20, 25, 30],
               "values": [3.366, 3.636, 3.877, 4.235, 4.553, 4.874, 5.193, 5.326, 5.307, 5.426],
               "kind": "par", "freq": 1},
    # Bundesbank zero curve subset, 2026-11-20
    "de_zero": {"tenors": [0.5, 1, 2, 3, 4, 5, 7, 10, 15, 20, 25, 30],
                "values": [2.83, 2.98, 3.08, 3.09, 3.10, 3.13, 3.23, 3.39, 3.58, 3.69, 3.75, 3.79],
                "kind": "zero", "freq": 1},
}
GRID = [0.5, 1, 2, 3, 5, 7, 10, 15, 20, 30]


def main():
    g = {"fits": {}, "risk": {}}
    for name, c in CASES.items():
        d = CurveData(np.array(c["tenors"], float), np.array(c["values"]) / 100, c["kind"], c["freq"])
        g["fits"][name] = {"input": c, "methods": {}}
        for m in ("ns", "nss", "spline", "cubic") + (("bootstrap",) if c["kind"] == "par" else ()):
            r = fit(m, d)
            g["fits"][name]["methods"][m] = {
                "rmse_bp": r.rmse_bp, "fitted": r.fitted.tolist(),
                "zero_grid": [float(r.curve.zero(t)) for t in GRID],
                "par_grid": [float(r.curve.par_yield(t, c["freq"])) for t in (2.0, 5.0, 10.0)],
            }
    curve = Svensson(0.042, -0.012, 0.015, -0.010, 1.6, 9.0)
    curves = {"g": curve}
    b = par_bond(curves, "g", 10.0, 2)
    st = curve_trade(curves, "g", 2.0, 10.0, 10_000, "steepener", freq=2)
    fly = butterfly(curves, "g", (2.0, 10.0), 5.0, 10_000, weighting="50/50", freq=2)
    shock = {"g": curve.key_rate_bumped([2.0, 10.0], [0.0, 0.0010])}
    g["risk"] = {
        "svensson": [0.042, -0.012, 0.015, -0.010, 1.6, 9.0],
        "bond10": {"coupon": b.coupon, "yield_dv01": b.yield_dv01(curves),
                   "zero_dv01": dv01(__import__("firv.risk", fromlist=["Trade"]).Trade([Leg(b, 1.0)]), curves)},
        "steepener": {"notionals": [l.notional for l in st.legs], "dv01": dv01(st, curves),
                      "krd": key_rate_dv01(st, curves)["g"].tolist(),
                      "carry_roll": {k: carry_roll(st, curves, 0.25)[k] for k in ("total", "carry", "roll")},
                      "scenario": scenario_pnl(st, curves, shock)["pnl"],
                      "scenario_h": scenario_pnl(st, curves, shock, 0.25)["pnl"]},
        "fly": {"notionals": [l.notional for l in fly.legs]},
        "boot_zero": [float(bootstrap_par(CASES["us_par"]["tenors"], np.array(CASES["us_par"]["values"]) / 100, 2).zero(t)) for t in GRID],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("window.GOLDEN = " + json.dumps(g) + ";\n")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
