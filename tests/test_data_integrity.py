"""Checks on the processed data. They run when data/processed exists (after the fetch
scripts) and are skipped on a fresh clone, which ships without data."""
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"


def need(*names):
    missing = [n for n in names if not (PROC / f"{n}.parquet").exists()]
    if missing:
        pytest.skip(f"processed data not built: {missing}")


def load(name):
    from firv.data.loaders import Panel
    return Panel.load(name).data


@pytest.mark.parametrize("params,zeros", [("de_params", "de_zero"), ("us_gsw_params", "us_gsw_zero"),
                                          ("ea_aaa_params", "ea_aaa_spot")])
def test_published_svensson_curves_are_continuously_compounded(params, zeros):
    need(params, zeros)
    from firv.curves import Svensson
    P, Z = load(params).dropna(), load(zeros)
    idx = P.index.intersection(Z.dropna(how="all").index)[::200]
    tenors = [2.0, 5.0, 10.0, 20.0]
    errs = []
    for d in idx:
        p = P.loc[d]
        c = Svensson(p.BETA0 / 100, p.BETA1 / 100, p.BETA2 / 100, p.BETA3 / 100, p.TAU1, p.TAU2)
        obs = Z.loc[d, tenors].to_numpy(float) / 100
        ok = ~np.isnan(obs)
        errs.append(np.max(np.abs(c.zero(np.array(tenors))[ok] - obs[ok])) * 1e4)
    assert np.median(errs) < 1.0          # bp; Bundesbank yields are rounded to 2 decimals


def test_yield_panels_are_in_plausible_ranges():
    for name in ("us_par", "de_zero", "fr_tec", "uk_nominal", "jp_par", "pl_par"):
        if not (PROC / f"{name}.parquet").exists():
            continue
        v = load(name).to_numpy(float)
        v = v[np.isfinite(v)]
        assert len(v) > 1000
        assert v.min() > -2.0 and v.max() < 25.0, name


def test_polish_coupons_reproduce_published_yields():
    p = PROC / "pl_coupons.csv"
    if not p.exists():
        pytest.skip("Polish curves not built")
    c = pd.read_csv(p)
    fixed = c[c.kind != "OK"]
    assert (fixed.check_bp < 2.0).mean() > 0.95
    # coupons are on a 0.25% grid when they pass the check
    ok = fixed[fixed.check_bp < 2.0]
    assert np.allclose((ok.coupon * 400).round(), ok.coupon * 400, atol=1e-6)


def test_constant_maturity_panels_never_difference_across_gaps():
    need("us_par")
    from firv import market as M
    from firv.curves.pca import changes_bp
    lv = M.cm_panel("US")[[1.0, 2.0, 5.0, 10.0, 30.0]]
    ch = changes_bp(lv)
    # each change spans at most 8 calendar days (the 30y gap of 2002-06 is never bridged)
    span = lv.index.to_series().diff().dt.days.reindex(ch.index)
    assert span.max() <= 8
